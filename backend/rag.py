import requests

from backend.retriever import Retriever


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"


class RAGPipeline:

    def __init__(self):

        print("Initializing RAG pipeline...")

        self.retriever = Retriever()

        print("RAG pipeline ready.")

    def generate_answer(self, question, top_k=5):

        # --------------------------------------------------
        # 1. Retrieve relevant chunks
        # --------------------------------------------------

        results = self.retriever.search(
            question,
            top_k=top_k
        )

        if not results:

            return {
                "answer": (
                    "I could not find relevant "
                    "information in the provided PDF."
                ),
                "citations": []
            }

        # --------------------------------------------------
        # 2. Build context
        # --------------------------------------------------

        context_parts = []

        for i, result in enumerate(results):

            context_parts.append(
                f"""
SOURCE {i + 1}
File: {result['source']}
Page: {result['page']}

{result['text']}
"""
            )

        context = "\n".join(context_parts)

        # --------------------------------------------------
        # 3. Prompt the LLM
        # --------------------------------------------------

        prompt = f"""
You are a PDF question-answering assistant.

Answer the user's question using ONLY the context
provided below.

Rules:

1. Do not use outside knowledge.
2. Do not invent facts.
3. Do not mention page numbers.
4. Do not create citations.
5. If the context does not contain the answer,
   say that you could not find the answer in the PDF.
6. Give a clear and concise answer.

CONTEXT:

{context}

QUESTION:

{question}

ANSWER:
"""

        # --------------------------------------------------
        # 4. Call Ollama
        # --------------------------------------------------

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        answer = data["response"].strip()

        # --------------------------------------------------
        # 5. Generate citations from retrieved metadata
        # --------------------------------------------------

        citations = []

        seen = set()

        for result in results:

            key = (
                result["source"],
                result["page"]
            )

            if key in seen:
                continue

            seen.add(key)

            citations.append({
                "source": result["source"],
                "page": result["page"],
                "score": round(
                    result["score"],
                    4
                )
            })

        # --------------------------------------------------
        # 6. Return answer + trusted citations
        # --------------------------------------------------

        return {
            "answer": answer,
            "citations": citations
        }