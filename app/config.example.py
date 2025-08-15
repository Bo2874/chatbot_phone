import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Thông tin kết nối tới Postgres
POSTGRES_HOST=YOUR_POSTGRES_HOST
POSTGRES_USER=YOUR_POSTGRES_USER
POSTGRES_DB=YOUR_POSTGRES_DB
POSTGRES_PASSWORD=YOUR_POSTGRES_PASSWORD

#Thông tin kết nối tới Milvus
URI_MILVUS = YOUR_URI_MILVUS
COLLECTION_NAME = YOUR_COLLECTION_NAME

# Cấu hình LLM 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")