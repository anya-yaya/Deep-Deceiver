from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(
    embedding_a,
    embedding_b
) -> float:
    """
    Calculate cosine similarity between two embeddings.
    """

    score = cosine_similarity(
        [embedding_a],
        [embedding_b]
    )[0][0]

    return float(score)