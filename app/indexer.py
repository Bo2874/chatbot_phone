
from typing import Any, Dict, List, Tuple
from langchain_milvus import Milvus, BM25BuiltInFunction
from embed import CustomHFEmbedding

from pymilvus import MilvusClient, DataType, Function, FunctionType


from langchain_core.documents import Document

def create_vectorstore( URI: str ,collection_name: str):
  """Create a vector store using Milvus and HuggingFace embeddings."""
  embeddings = CustomHFEmbedding()
  vector_store = Milvus(
      auto_id=False,
      embedding_function=embeddings,
      builtin_function = BM25BuiltInFunction(),
      vector_field = ["vector", "sparse"],
      connection_args={"uri": URI},
      collection_name = collection_name
  )
  return vector_store

class IndexService:
    def __init__(self, URI: str, collection_name: str ):
        self.uri = URI
        self.collection_name= collection_name
        self.create_vector_store_if_no_exist()
        self.vector_store = create_vectorstore(URI,collection_name)
    
    def create_vector_store_if_no_exist(self):
        # Khởi tạo client
        client = MilvusClient(uri=self.uri)

        # Kiểm tra xem đã tồn tại collection hay chưa
        if client.has_collection(self.collection_name):
            return

        # Tạo schema 
        schema = MilvusClient.create_schema(enable_dynamic_field=True)

        # Các trường cơ bản
        schema.add_field(
            field_name="id",
            datatype=DataType.INT64,
            is_primary=True,
            description="khóa chính"
        )
        schema.add_field(
            field_name="text",
            datatype=DataType.VARCHAR,
            max_length=65535,
            enable_analyzer=True,
            description="văn bản để embedding"
        )
        schema.add_field(
            field_name="sparse",
            datatype=DataType.SPARSE_FLOAT_VECTOR,
            nullable=False,
            description="sparse vector được tự động tạo từ BM25"
        )
        schema.add_field(
            field_name="vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=1024,
            nullable=False,
            description="vector embedding của text"
        )

        # Định nghĩa function BM25 cho trường "text" → "sparse"
        bm25_function = Function(
            name="text_bm25_emb",
            input_field_names=["text"],
            output_field_names=["sparse"],
            function_type=FunctionType.BM25,
        )
        schema.add_function(bm25_function)

        # Chuẩn bị index để tăng tốc độ tìm kiếm
        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_name="vector_flat_idx",
            index_type="FLAT",
            metric_type="COSINE",
        )
        index_params.add_index(
            field_name="sparse",
            index_name="sparse_idx",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="BM25",
        )

        # Tạo collection
        client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        
    def store_chunks(self, chunks: list[Document]):
        """Store chunks in the vector store."""
        self.vector_store.add_documents(chunks)
    
# from conn_postgres import pg_conn, pg_cursor

# pg_cursor.execute("SELECT id, raw_text FROM raw_texts;")
# rows = pg_cursor.fetchall()
# documents = []
# for row in rows:
#     doc = Document(
#         page_content=row[1],   # content
#         metadata={"id": row[0]}  # lưu id để truy vết
#     )
#     documents.append(doc)

# pg_cursor.close()
# pg_conn.close()

# # Khởi tạo dịch vụ
# index_service = IndexService(
#     URI="http://localhost:19530",
#     collection_name="phone_vectors"
# )
# # Lưu vào Milvus
# index_service.store_chunks(documents)
# print("✅ Đã thêm vào Milvus")