from router import router
from conn_postgres import pg_conn, pg_cursor
from vector_search import VectorSearchAgent, get_texts_by_ids
from config import OPENAI_API_KEY
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from rewrite_query import rewrite_query_for_search
from milvus_connection import vector_store # Gọi file để tránh khởi tại và kết nối tới milvus nhiều lần
from logging_config import setup_logging
import time
import json
import os

#Load data về thông tin cửa hàng
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, '..', 'data', 'store_data.json')

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)


logger = setup_logging()


llm = ChatOpenAI(
        model="gpt-4.1-nano-2025-04-14",
        temperature=1,
        openai_api_key=OPENAI_API_KEY,
        streaming = True
)

llm_SQL = ChatOpenAI(
            model="gpt-4.1-nano-2025-04-14",
            temperature=0,
            openai_api_key=OPENAI_API_KEY
)

# Hàm chính xử lý câu hỏi khách hàng
async def streaming_chatbot(query: str, history: list[dict]):
    logger.info(query)

    start_time1 = time.time()
    new_query = rewrite_query_for_search(query, history)
    end_time1 = time.time()
    logger.info(new_query)
    logger.info(f"Tổng thời gian phản hồi của rewrite: {(end_time1 - start_time1):.2f} giây")
    
    start_time2 = time.time()
    intend = router(new_query)
    end_time2 = time.time()
    logger.info(intend)
    logger.info(f"Tổng thời gian phản hồi của router: {(end_time2 - start_time2):.2f} giây")
    

    system_msg = SystemMessage(
        content="Bạn là 1 nhân viên tư vấn điện thoại cho cửa hàng Bộ Mobile."
    )

    # Chuyển history dạng dict -> message
    history_messages = []
    for msg in history[-4:]:  # chỉ lấy 4 tin nhắn gần nhất
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            history_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            history_messages.append(AIMessage(content=content))
    
    messages = []

    if intend == "Hỏi đáp về chatbot":
        human_msg = HumanMessage(
            content = (
                f"""**Đây là truy vấn của người dùng:**{query}
                Dựa vào thông tin cửa hàng để trả lời truy vấn người dùng
                Đây là các thông tin của cửa hàng: 
                {data}

                Nguyên tắc:
                - Chỉ trả lời dựa trên thông tin trên.
                - Nếu không tìm thấy thông tin trong JSON, hãy trả lời: "Xin lỗi, tôi chưa có thông tin này."

                **Yêu cầu định dạng:**
                *Sử dụng markdown tại những ý chính để trả lời.*
                """
            )
        )
        messages = [system_msg] + history_messages + [human_msg]

    elif intend == "Chào hỏi khách hàng":
        human_msg = HumanMessage(
            content = (
                f"""**Đây là truy vấn của người dùng:**{query}
                Hãy chào lại khách hàng và hỏi khách hàng tương tự như sau:
                - Xin chào bạn, mình có thể hỗ trợ gì cho bạn không? Bạn có đang quan tâm đến dòng điện thoại nào không?

                **Yêu cầu định dạng:**
                **Sử dụng markdown tại các danh từ.**
                """
            )
        )
        messages = [system_msg] + history_messages + [human_msg]

    elif intend == "Tư vấn sản phẩm dùng SQL":
        prompt_SQL = f"""
        Bạn là một chuyên gia viết câu lệnh Postgres SQL. Hãy dựa vào câu hỏi sau để chuyển nó thành câu truy vấn SQL truy vấn vào bảng `products` và `colors`.

        Thông tin bảng `products` gồm:
        - brand
        - name
        - screen_tech
        - screen_size (REAL)
        - camera (REAL)
        - os
        - storage (REAL)
        - ram (REAL)
        - battery (REAL)
        - price (REAL)

        Bảng `colors` gồm:
        - product_id
        - color

        Câu hỏi người dùng:
        \"\"\"{new_query}\"\"\"

        Trả về:
        ví dụ 1: SELECT * FROM products
                 WHERE brand ILIKE 'Samsung'
                 ORDER BY battery DESC
                 LIMIT 1;
        ví dụ 2: SELECT * FROM products
                 WHERE brand ILIKE 'Apple'
                 AND price BETWEEN 10000000 AND 15000000;
        ví dụ 3: SELECT p.*, c.color
                 FROM products p
                 LEFT JOIN colors c ON p.id = c.product_id
                 WHERE p.brand ILIKE '%Nokia%'
                 AND p.name ILIKE '%3210 4G%'
        ví dụ 4: SELECT DISTINCT brand FROM products;

        *Lưu ý:
        Đặt LIMIT tối đa = 10.
        Pin trâu được hiểu là battery >= 4000
        Thương hiệu của điện thoại iPhone là Apple (brand ILIKE 'Apple')

        Chỉ trả về mã SQL như ví dụ, không giải thích gì thêm.
        """


        start_time = time.time()
        sql = await llm_SQL.ainvoke([HumanMessage(content=prompt_SQL)])
        end_time = time.time()
        print("Truy vấn:", sql.content)
        logger.info(f"Tổng thời gian phản hồi sinh SQL: {(end_time - start_time):.2f} giây")

        start_time_sql = time.time()
        pg_cursor.execute(sql.content)
        rows = pg_cursor.fetchall()
        columns = [descrip[0] for descrip in pg_cursor.description]
        results_str = "\n".join(
            [", ".join(f"{col}: {val}" for col, val in zip(columns, row)) for row in rows]
        )
        end_time_sql = time.time()
        logger.info(f"Tổng thời gian phản hồi truy suất SQL: {(end_time_sql - start_time_sql):.2f} giây")
        
        human_msg = HumanMessage(
            content = (
                f"""**Đây là truy vấn của người dùng:**{new_query}
                **Đây là thông tin đã truy xuất được từ cơ sở dữ liệu:**\n{results_str}\n\n
                Dựa vào thông tin trên, bạn hãy trả lời câu hỏi từ người dùng một cách đầy đủ, rõ ràng và thân thiện. Không cần thêm 'Chào bạn!' vào đầu câu trả lời.
                Nếu không có kết quả, trả về: "Hiện tại chúng tôi chưa cập nhật dữ liệu mà bạn đang hỏi, bạn có thể tham khảo một số dòng điện thoại khác".

                **Yêu cầu định dạng:**
                * Câu đầu tiên là câu dẫn. 
                * Sử dụng danh sách gạch đầu dòng (*) để liệt kê các thông tin của sản phẩm.
                * Sau khi liệt kê xong thì cách ra 1 dòng và token tiếp theo phải được in ra ở đầu dòng bằng với dòng đầu tiên.
                * Sử dụng in đậm (**) cho các từ khóa quan trọng.
                **KHÔNG được trả về giá tiền dạng chữ.**
                **Ở cuối phản hồi thêm đoạn sau bằng dạng chữ in đậm: Bạn có thể đến trực tiếp cửa hàng hoặc liên hệ qua hotline 0987 789 987 để được tư vấn chọn dòng phù hợp nhất và nhận các ưu đãi hấp dẫn.**
                """
            )
        )
        messages = [system_msg] + history_messages + [human_msg]

    elif intend == "Tư vấn sản phẩm dùng vector search":

        start_time = time.time()
        retriever = VectorSearchAgent(vector_store)
        ids = retriever.retrieve(new_query, 4)
        infors = get_texts_by_ids(ids)
        end_time = time.time()
        logger.info(f"Tổng thời gian phản truy suất vector: {(end_time - start_time):.2f} giây")
        
        human_msg = HumanMessage(
            content = (
                f"""**Đây là truy vấn của người dùng:**{new_query}
                **Đây là thông tin đã truy xuất được từ cơ sở dữ liệu:**\n{infors}\n\n
                Dựa vào thông tin trên, bạn hãy trả lời câu hỏi từ người dùng một cách đầy đủ, rõ ràng và thân thiện. Không cần thêm 'Chào bạn!' vào đầu câu trả lời.
                Nếu không có kết quả, trả về: "Hiện tại chúng tôi chưa cập nhật dữ liệu mà bạn đang hỏi, bạn có thể tham khảo một số dòng điện thoại khác".

                **Yêu cầu định dạng:**
                * Câu đầu tiên là câu dẫn. 
                * Sử dụng danh sách gạch đầu dòng (*) để liệt kê các thông tin của sản phẩm.
                * Sau khi liệt kê xong thì cách ra 1 dòng và token tiếp theo phải được in ra ở đầu dòng bằng với dòng đầu tiên.
                * Sử dụng in đậm (**) cho các từ khóa quan trọng.
                **Ở cuối phản hồi thêm đoạn sau bằng dạng chữ in đậm: Bạn có thể đến trực tiếp cửa hàng hoặc liên hệ qua hotline 0987 789 987 để được tư vấn chọn dòng phù hợp nhất và nhận các ưu đãi hấp dẫn.**
                """
            )
        )
        messages = [system_msg] + history_messages + [human_msg]

    else: #intend == "Trò chuyện phiếm"
        human_msg = HumanMessage(
            content = (
                f"""**Đây là truy vấn của người dùng:**{query}
                Hãy nói truyện với người dùng 1 cách bình thường.

                **Yêu cầu định dạng:**
                *Hạn chế sử dụng icon để trả lời.
                """
            )
        )
        messages = [system_msg] + history_messages + [human_msg]

    # Biến cờ để kiểm tra token đầu tiên
    first_token_received = False
    start_time = time.time()
    # Stream token
    async for chunk in llm.astream(messages):
        if chunk.content:
            if not first_token_received:
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.info(f"Thời gian nhận token đầu tiên (TTFT): {elapsed_time:.2f} giây")
                # Đặt cờ thành True để không chạy lại khối này nữa
                first_token_received = True
            yield chunk.content     #Khi dùng return hàm sẽ kết thúc ngay lập tức, trả về 1 giá trị duy nhất
                                    # yeild hàm tạm dừng, trả về 1 giá trị, và có thể tiếp tục từ chỗ đã dừng vào lần gọi tiếp theo
    
    

