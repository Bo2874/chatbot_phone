import ast
import re
import pandas as pd

def join_string(item):
  for i in range(len(item)):
    title, product_promotion, product_specs, current_price, color_options = item

    final_string = ""
    if title:
      final_string += f"{title}"
    if product_promotion:
      product_promotion = product_promotion.replace("<br>", " ").replace("\n", " ")
      final_string += f" {product_promotion}"
    if product_specs:
      product_specs = product_specs.replace("<br>", " ").replace("\n", " ")
      final_string += f" {product_specs}"
    if current_price:
      final_string += f" có giá: {current_price}"
    if color_options:
      final_string += f" có màu sắc: "
      colors = ast.literal_eval(color_options)
      final_string += ", ".join(colors)

  return final_string

def preprocess_text(text: str) -> str:
    """
    Hàm tiền xử lý cơ bản cho văn bản.
    """
    # 1. Chuyển về chữ thường
    text = text.lower()

    # 2. Xóa khoảng trắng thừa (nhiều khoảng trắng thành một, xóa ở đầu/cuối)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

df = pd.read_csv(r'C:\chatbot_phone\data\hoanghamobile.csv')
df = df.drop(columns='_id')
df['information'] = df[
    [
        'title',
        'product_promotion',
        'product_specs',
        'current_price',
        'color_options'
    ]
].astype(str).apply(join_string, axis=1)

phone_data_chunks = df['information'].astype(str).tolist()
preprocessed_data_chunks = [preprocess_text(chunk) for chunk in phone_data_chunks]

# print(f"Dòng đầu: {preprocessed_data_chunks[0]}")

