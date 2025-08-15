from langchain_core.documents import Document
from conn_postgres import pg_conn, pg_cursor


hybrid_search_params = [
    {
        "anns_field": "vector",    # Trường vector dày (dense)
        "metric_type": "COSINE",   # Metric cho vector dày
        "params": {
            "ef": 64,              # Độ chính xác tìm kiếm (càng cao càng chính xác nhưng chậm hơn)
            "nprobe": 16           # Số lượng cluster để tìm kiếm (tương tự nprobe trong IVF)
        }
    },
    {
        "anns_field": "sparse",    # Trường vector thưa (sparse)
        "metric_type": "BM25",     # Metric BM25 cho vector thưa  
        "params": {
            "k1": 1.2,             # Tham số k1 của BM25 (thường từ 1.2-2.0)
            "b": 0.7              # Tham số b của BM25 (thường từ 0.5-0.8)
        }
    }
]
class VectorSearchAgent:
    def __init__(self, vector_store):
        """Initialize the Retriever with a vector store."""
        self.vector_store = vector_store
        self.search_params = hybrid_search_params
    def retrieve(self, query: str, top_k: int) -> list[str]:
        """Retrieve document ids from the vector store based on the query."""
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k,
                param=self.search_params,
                ranker_type="weighted",
                ranker_params={"weights": [0.6, 0.4]}
            )
            # Extract only ids from Document.metadata["id"]
            ids = [doc.metadata["id"] for doc, score in results]
            return ids
        except Exception as e:
            print("Search error:", e)
            return []


def get_texts_by_ids(ids: list[str]) -> list[dict]:
    """Lấy dữ liệu từ PostgreSQL theo danh sách ids"""
    
    sql = "SELECT id, raw_text FROM raw_texts WHERE id = ANY(%s);"
    pg_cursor.execute(sql, (ids,))
    rows = pg_cursor.fetchall()

    results = [{"id": row[0], "text": row[1]} for row in rows]

    return results   
    
# if __name__ == "__main__":
#     # Example usage
#     from indexer import create_vectorstore
#     from milvus_connection import vector_store

#     retriever = VectorSearchAgent(vector_store)
    
#     query = "giá điện thoại nokia 3210"
#     ids = retriever.retrieve(query, top_k=2)
#     results = get_texts_by_ids(ids)
#     print(results)