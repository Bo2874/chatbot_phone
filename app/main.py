from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot import streaming_chatbot  # hàm đã được sửa để yield từng chữ
from fastapi.responses import StreamingResponse

app = FastAPI()

class Query(BaseModel):
    question: str
    history: list[dict]

@app.post("/chat")
async def chat(query: Query):
    async def response_stream():
        async for chunk in streaming_chatbot(query.question, query.history):
            yield chunk.encode("utf-8")

    return StreamingResponse(response_stream(), media_type="text/plain")
