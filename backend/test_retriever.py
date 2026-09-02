from backend.retriever import Retriever


retriever = Retriever()


question = input(
    "\nEnter your question: "
)


results = retriever.search(
    question,
    top_k=5
)


print("\n" + "=" * 70)
print("RETRIEVED CHUNKS")
print("=" * 70)


for i, result in enumerate(results):

    print(
        f"\n[{i + 1}] "
        f"Score: {result['score']:.4f}"
    )

    print(
        f"Source: {result['source']}"
    )

    print(
        f"Page: {result['page']}"
    )

    print(
        f"\n{result['text'][:700]}"
    )