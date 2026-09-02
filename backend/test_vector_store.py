from backend.vector_store import load_vector_store


index, metadata = load_vector_store()


print("FAISS vectors:", index.ntotal)
print("Metadata records:", len(metadata))


print("\nFirst metadata record:")
print(metadata[0])