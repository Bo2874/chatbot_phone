from data_preprocessing import preprocessed_data_chunks
from conn_postgres import pg_conn, pg_cursor

# Insert toàn bộ data vào postgresSQL
data_to_insert = [(text, ) for text in preprocessed_data_chunks]
pg_cursor.executemany("INSERT INTO raw_texts (raw_text) VALUES (%s)", data_to_insert)
pg_conn.commit() 
print("OK")

pg_cursor.close()
pg_conn.close()