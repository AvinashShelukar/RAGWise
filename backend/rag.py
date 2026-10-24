
import json
import re
import urllib.error
import urllib.request

from backend.retriever import Retriever


MODEL_NAME = "qwen2.5:7b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


class RAGPipeline:

    def __init__(self):
        print("Initializing RAG pipeline...")

        self.retriever = Retriever()

        print(f"Using local Ollama model: {MODEL_NAME}")
        print("RAG pipeline ready.")

    def select_document(self, question):
        question_lower = question.lower()

        # Select a PDF explicitly mentioned in the question.
        for document in self.retriever.documents:
            if document.lower() in question_lower:
                return document

        # Automatically select only when there is one PDF.
        if len(self.retriever.documents) == 1:
            return self.retriever.documents[0]

        # Never guess which PDF the user means.
        return None
    @staticmethod
    def clean_answer(answer):
        """Clean terminal artifacts and common spacing issues."""

        if not answer:
            return ""

        # Remove ANSI terminal escape sequences.
        answer = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])",
            "",
            answer
        )

        # Restore spaces accidentally omitted between common words.
        answer = re.sub(
            r"\b(systematic)(review)\b",
            r"\1 \2",
            answer,
            flags=re.IGNORECASE
        )

        # Normalize spaces and newlines.
        answer = re.sub(r"[ \t]+", " ", answer)
        answer = re.sub(r" *\n *", "\n", answer)
        answer = re.sub(r"\n{3,}", "\n\n", answer)

        return answer.strip()


    def generate_answer(self, question, top_k=5, source=None):
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        question = question.strip()

        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20.")

        selected_document = source or self.select_document(question)

        if (
            selected_document
            and selected_document not in self.retriever.documents
        ):
            raise ValueError(
                f"Unknown PDF: {selected_document}. "
                f"Available PDFs: {', '.join(self.retriever.documents)}"
            )

        # Retrieve relevant chunks.
        results = self.retriever.search(
            question,
            top_k=top_k,
            source=selected_document
        )

        if not results:
            return {
                "answer": (
                    "I could not find relevant information "
                    "in the selected PDFs."
                ),
                "citations": []
            }

        # Build context with source filenames and page numbers.
        context_parts = []

        for i, item in enumerate(results, start=1):
            context_parts.append(
                f"SOURCE {i}\n"
                f"File: {item['source']}\n"
                f"Page: {item['page']}\n"
                f"Content:\n{item['text']}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a precise PDF question-answering assistant.

Answer the question using ONLY the supplied context.

Rules:
1. Answer the question directly and clearly.
2. Do not use outside knowledge or invent facts.
3. Write natural, grammatically correct sentences.
4. Do not repeat words, phrases, or sentences.
5. Do not copy corrupted or duplicated text from the context.
6. Summarize the relevant information in your own words.
7. If the context does not contain the answer, say:
   "I could not find the answer in the provided PDF."
8. Do not invent page numbers or citations.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        # Generate using Ollama's local HTTP API.
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 512
            }
        }

        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=180
            ) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as error:
            details = error.read().decode(
                "utf-8", errors="replace"
            )
            raise RuntimeError(
                f"Ollama HTTP error {error.code}: {details}"
            ) from error

        except urllib.error.URLError as error:
            raise RuntimeError(
                "Could not connect to Ollama. "
                "Check that Ollama is running locally. "
                f"Details: {error}"
            ) from error

        except TimeoutError as error:
            raise RuntimeError(
                "Ollama generation timed out after 180 seconds."
            ) from error

        except json.JSONDecodeError as error:
            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from error

        answer = self.clean_answer(data.get("response", ""))

        if not answer:
            raise RuntimeError("Ollama returned an empty answer.")

        # Prepare unique source-page citations.
        citations = []
        seen = set()

        for item in results:
            key = (item["source"], item["page"])

            if key in seen:
                continue

            seen.add(key)

            citations.append({
                "source": item["source"],
                "page": item["page"],
                "score": round(float(item["score"]), 4)
            })

        return {
            "answer": answer,
            "citations": citations
        }
