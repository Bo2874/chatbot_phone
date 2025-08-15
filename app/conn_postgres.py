import psycopg2
from config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

# --- Kết nối PostgreSQL --- 
pg_conn = psycopg2.connect(
    host=POSTGRES_HOST,
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)
pg_cursor = pg_conn.cursor() #Tạo một đối tượng cursor(con trỏ) để làm việc với database (truy vấn, insert, update, ...).
