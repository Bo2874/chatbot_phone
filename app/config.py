import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Thông tin kết nối tới Postgres
POSTGRES_HOST="localhost"
POSTGRES_USER="postgres"
POSTGRES_DB="postgres"
POSTGRES_PASSWORD="28072004"

#Thông tin kết nối tới Milvus
URI_MILVUS = "http://localhost:19530"
COLLECTION_NAME = "phone_vectors"

# Cấu hình LLM 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

