from indexer import create_vectorstore
from config import URI_MILVUS, COLLECTION_NAME

URI = URI_MILVUS
collection_name = COLLECTION_NAME

# Tạo vector store để truy suất thông tin 
vector_store = create_vectorstore(URI, collection_name)