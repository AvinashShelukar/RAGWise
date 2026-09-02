from backend.rag import RAGPipeline


rag = RAGPipeline()


question = input(
    "\nAsk a question about your PDF: "
)


result = rag.generate_answer(
    question,
    top_k=5
)


print("\n")
print("=" * 70)
print("ANSWER")
print("=" * 70)

print(result["answer"])


print("\n")
print("=" * 70)
print("CITATIONS")
print("=" * 70)


for citation in result["citations"]:

    print(
        f"📄 {citation['source']} "
        f"- Page {citation['page']} "
        f"(score={citation['score']:.4f})"
    )