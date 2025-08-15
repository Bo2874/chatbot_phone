from config import OPENAI_API_KEY
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI


def rewrite_query_for_search(query: str, history: list[dict]):
    # Chuyển history dạng dict -> message
    history_messages = []
    for msg in history[-4:]:  # chỉ lấy 4 tin nhắn gần nhất
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            history_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            history_messages.append(AIMessage(content=content))


    system_msg = SystemMessage(
        content = 'Bạn là 1 chuyên gia viết lại truy vấn gần nhất của người dùng.'
    )
    human_msg = HumanMessage(
        content = f"""
        **Đây là truy vấn gần nhất từ người dùng:**{query}.
        *Những chủ đề truy vấn sau sẽ giữ nguyên và không cần viết lại: 
        ['chào hỏi', 'nói truyện phiếm', 'hỏi về tác dụng chatbot của cửa hàng'].*
    
        **Nguyên tắc trả về**
        *Không được tự ý bịa thêm.*
        *Nếu thấy lịch sử trò truyện có bổ sung thông tin cho truy vấn thì hãy viết lại truy vấn.*
        *Chỉ trả về 1 câu truy vấn duy nhất, không giải thích gì thêm.*
        """
    )

    # Tạo prompt
    messages = [system_msg] + history_messages + [human_msg]

    # Khởi tạo model có stream
    llm = ChatOpenAI(
        model="gpt-4.1-nano-2025-04-14",  #gpt-5-nano-2025-08-07
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    )

    res = llm.invoke(messages)
    return res.content