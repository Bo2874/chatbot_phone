from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import OPENAI_API_KEY

def router(user_input: str):
    system_msg = SystemMessage(
        content = "Bạn là mô hình phân loại truy vấn dựa vào sự tương đồng về mặt ngữ nghĩa trong 5 chủ đề."
    )

    human_msg = HumanMessage(
        content = (
            f"""
            **Đây là truy vấn của người dùng:** {user_input}

            Đây là 5 chủ đề bạn cần phân loại:

            **Hỏi đáp về chatbot** : 
            Câu truy vấn liên quan đến hỏi thông tin và tác dụng của chatbot, hỏi về các thông tin và dịch vụ liên quan đến cửa hàng.
            Example:  
            - Bạn là ai?  
            - Tác dụng của bạn là gì?  
            - Giờ mở cửa của cửa hàng
            - Chính sách bảo hành bên bạn như thế nào?
            - Địa chỉ cửa hàng của bạn ở đâu
            - Bên bạn có những dòng điện thoại nào
            - Bên shop có những loại điện thoại nào
            
            **Chào hỏi khách hàng**:
            Câu truy vấn liên quan đến chào hỏi.
            Example:  
            - Hi  
            - Hello  
            - Chào shop  
            - Chào bạn  
            - Cho mình hỏi tí  
    
            **Tư vấn sản phẩm dùng SQL**: 
            Câu truy vấn liên quan đến các số liệu cụ thể như là giá, pin, hoặc tìm những cái nhất.
            Example:  
            - Điện thoại nào pin trâu dưới 5 triệu?  
            - Mẫu nào có camera 64MP?  
            - Tôi muốn tìm điện thoại RAM 8GB, pin 5000mAh  
            - Bên bạn máy nào có camera tốt nhất  
            - Bên bạn có những hãng điện thoại nào  
            - Điện thoại X có những màu gì

            **Tư vấn sản phẩm dùng vector search**: 
            Câu truy vấn liên quan đến hỏi thông tin về điện thoại bất kì một cách chung chung.
            Example:  
            - Tư vấn mẫu tương tự iPhone 13  
            - Có mẫu nào tương đồng với Samsung A23 không?  
            - Tôi muốn biết thông tin về điện thoại Samsung Galaxy S23 và các chương trình khuyến mãi của máy  

            **Trò chuyện phiếm**:  
            Câu truy vấn không liên quan đến 4 chủ đề nêu trên.
            Example:  
            - Hôm nay mệt quá  
            - Bạn biết đùa không?  
            - Kể tôi một chuyện vui đi  
            - Bạn biết làm thơ không

            **Nguyên tắc trả về**
            *So sánh giữa truy vấn và Example để phân loại**
            *Bạn cần phân loại truy vấn của người dùng vào **một** trong 5 chủ đề trên.* 
            *Nếu câu truy vấn không thuộc chủ đề nào, hãy chọn: **Trò chuyện phiếm*.  
            *Chỉ trả về tên của chủ đề, không giải thích gì thêm.*
            """
        )
    )

    prompt = [system_msg] + [human_msg]

    llm = ChatOpenAI(
        model="gpt-5-nano-2025-08-07", #gpt-5-nano-2025-08-07
        temperature=1,
        openai_api_key=OPENAI_API_KEY
    )

    res = llm.invoke(prompt)
    return res.content

# q = "Tôi muốn biết thông tin về điện thoại samsung"
# print(router(q))