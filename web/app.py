import streamlit as st
import requests
import time

# --- Cấu hình trang ---
st.set_page_config(page_title="Chatbot Tư Vấn Điện Thoại", page_icon="💬", layout="wide")

# --- Khởi tạo Session State ---
# Cấu trúc session state để quản lý nhiều cuộc hội thoại
# `chat_sessions` là một danh sách, mỗi phần tử là một cuộc hội thoại (cũng là một danh sách các tin nhắn)
if "chat_sessions" not in st.session_state:
    # Bắt đầu với một cuộc hội thoại trống
    st.session_state.chat_sessions = [[]] 
if "active_chat_idx" not in st.session_state:
    # Chỉ số của cuộc hội thoại đang hoạt động
    st.session_state.active_chat_idx = 0

# --- Sidebar để quản lý các cuộc hội thoại ---
with st.sidebar:
    st.title("📝 Cuộc hội thoại")
    
    # Nút để tạo cuộc hội thoại mới
    if st.button("➕ Tạo cuộc hội thoại mới"):
        st.session_state.chat_sessions.append([])
        # Chuyển sang cuộc hội thoại mới vừa tạo
        st.session_state.active_chat_idx = len(st.session_state.chat_sessions) - 1
        st.rerun() # Chạy lại script để cập nhật giao diện

    st.markdown("---")

    # Hiển thị danh sách các cuộc hội thoại để chọn
    # Dùng st.radio để chọn, khi chọn sẽ tự động chạy lại script
    # và cập nhật `active_chat_idx`
    st.session_state.active_chat_idx = st.radio(
        "Chọn một cuộc hội thoại:",
        range(len(st.session_state.chat_sessions)),
        format_func=lambda i: f"Cuộc hội thoại #{i + 1}",
        index=st.session_state.active_chat_idx,
        label_visibility="collapsed" # Ẩn label "Chọn một cuộc hội thoại:"
    )

    st.markdown("---")

    # Nút để xóa cuộc hội thoại hiện tại
    if st.button("🗑️ Xóa cuộc hội thoại này", type="secondary"):
        # Chỉ xóa nếu còn nhiều hơn 1 cuộc hội thoại
        if len(st.session_state.chat_sessions) > 1:
            st.session_state.chat_sessions.pop(st.session_state.active_chat_idx)
            # Chuyển về cuộc hội thoại đầu tiên sau khi xóa để tránh lỗi index
            if st.session_state.active_chat_idx >= len(st.session_state.chat_sessions):
                st.session_state.active_chat_idx = len(st.session_state.chat_sessions) - 1
        else:
            # Nếu chỉ còn 1, thì chỉ xóa nội dung của nó
            st.session_state.chat_sessions[0] = []
        st.rerun()

# --- Giao diện Chat chính ---
st.title(f"💬 Chatbot Bộ Mobile - Cuộc hội thoại #{st.session_state.active_chat_idx + 1}")

# Lấy ra cuộc hội thoại đang hoạt động dựa trên chỉ số
active_chat = st.session_state.chat_sessions[st.session_state.active_chat_idx]

# 1. Hiển thị các tin nhắn đã có trong cuộc hội thoại đang hoạt động
for message in active_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Chờ đợi và xử lý input mới của người dùng
if prompt := st.chat_input("Nhập câu hỏi của bạn ..."):
    # Thêm tin nhắn của người dùng vào lịch sử của cuộc hội thoại hiện tại
    active_chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Hiển thị câu trả lời của bot với hiệu ứng streaming
    with st.chat_message("assistant"):
        bot_placeholder = st.empty()
        # Hiển thị một thông báo chờ tạm thời trong khi gọi API
        bot_placeholder.markdown("Đang suy nghĩ...")
        full_response = ""

        # Chuẩn bị history để gửi cho API (lấy 4 tin nhắn gần nhất)
        history_for_api = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in active_chat[-5:-1] # Lấy 4 tin nhắn trước tin nhắn hiện tại
        ]

        try:
            # --- GỌI API THẬT CỦA BẠN ---
            # Sử dụng with để đảm bảo kết nối được đóng đúng cách
            with requests.post(
                "http://localhost:8000/chat", 
                json={
                    "history": history_for_api,
                    "question": prompt
                }, 
                stream=True, 
                timeout=300
            ) as response:
                # Báo lỗi nếu request không thành công (vd: lỗi 4xx, 5xx)
                response.raise_for_status() 
                # Dùng iter_content để xử lý streaming an toàn hơn
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        # Thêm con trỏ nhấp nháy để tạo cảm giác "đang gõ"
                        bot_placeholder.markdown(full_response + "▌")

            # Cập nhật placeholder lần cuối để xóa con trỏ
            bot_placeholder.markdown(full_response)

        except requests.exceptions.RequestException as e:
            full_response = f"**Lỗi:** Không thể kết nối tới máy chủ. Vui lòng kiểm tra lại backend và thử lại.\n\n*Chi tiết lỗi: {e}*"
            bot_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"**Lỗi:** Một lỗi không xác định đã xảy ra.\n\n*Chi tiết lỗi: {e}*"
            bot_placeholder.markdown(full_response)


    # Thêm câu trả lời hoàn chỉnh của bot vào lịch sử của cuộc hội thoại hiện tại
    active_chat.append({"role": "assistant", "content": full_response})