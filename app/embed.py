from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

class CustomHFEmbedding(Embeddings):
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.model.encode(text).tolist() for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()
