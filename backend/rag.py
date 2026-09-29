import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from backend.retriever import Retriever


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_NAME = "deepseek-ai/DeepSeek-R1:fastest"


class RAGPipeline:

    def __init__(self):

        print("Initializing RAG pipeline...")

        if not HF_TOKEN:
            raise RuntimeError(
                "HF_TOKEN is not set. "
                "Add it to the environment variables."
            )

        self.retriever = Retriever()

        self.client = InferenceClient(
            token=HF_TOKEN
        )

        print("RAG pipeline ready.")

    def generate_answer(self, question, top_k=5):

        # --------------------------------------------------
        # Retrieve relevant chunks
        # --------------------------------------------------

        results = self.retriever.search(
            question,
            top_k=top_k
        )

        if not results:

            return {
                "answer": (
                    "I could not find relevant information "
                    "in the provided PDF."
                ),
                "citations": []
            }

        # --------------------------------------------------
        # Build context
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
        # Prompt
        # --------------------------------------------------

        prompt = f"""
Answer the user's question using ONLY the context below.

Rules:
1. Use only information from the supplied context.
2. Do not use outside knowledge.
3. Do not invent facts.
4. Do not mention page numbers in the answer.
5. Give a concise and clear answer.
6. If the answer is not present in the context, say:
   "I could not find the answer in the provided PDF."

CONTEXT:

{context}

QUESTION:

{question}

ANSWER:
"""

        # --------------------------------------------------
        # Hugging Face generation
        # --------------------------------------------------

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are RAGWise, a PDF question-answering "
                        "assistant. Answer only from the supplied "
                        "document context."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500
        )

        # --------------------------------------------------
        # Extract answer
        # --------------------------------------------------

        answer = response.choices[0].message.content.strip()

        # Remove DeepSeek reasoning section
        if "<think>" in answer and "</think>" in answer:

            answer = answer.split(
                "</think>",
                1
            )[1].strip()

        # --------------------------------------------------
        # Citations
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

            citations.append(
                {
                    "source": result["source"],
                    "page": result["page"],
                    "score": round(
                        result["score"],
                        4
                    )
                }
            )

        # --------------------------------------------------
        # Final response
        # --------------------------------------------------

        return {
            "answer": answer,
            "citations": citations
        }