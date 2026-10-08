from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str):
    """
    Convert text into a semantic embedding.
    """

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding