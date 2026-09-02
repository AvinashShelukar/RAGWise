from backend.embeddings import EmbeddingModel


model = EmbeddingModel()

texts = [
    "Malware detection using artificial intelligence.",
    "Explainable AI helps understand model predictions."
]

embeddings = model.encode(texts)

print("\nNumber of embeddings:", len(embeddings))

print(
    "Embedding dimension:",
    embeddings.shape[1]
)

print(
    "First embedding:",
    embeddings[0][:10]
)