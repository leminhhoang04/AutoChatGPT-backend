from typing import Union

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel

from auto_chatgpt import AutoChatGPT


app = FastAPI()
auto_chat_gpt = AutoChatGPT()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class ChatRequest(BaseModel):
    question: str
    password: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.put("/screenshot")
def take_screenshot():
    try:
        auto_chat_gpt.take_screenshot()
        return {"message": "Screenshot taken successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = auto_chat_gpt.send_request(request.question, request.password)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/chat_w_image")
async def chat_w_image(
    question: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(..., description="Support .png file")
):
    try:
        request = ChatRequest(question=question, password=password)
        file_content_bytes = await file.read()

        await auto_chat_gpt.upload_file_to_chat(file_content_bytes, request.password)
        response = auto_chat_gpt.send_request(request.question, request.password)
        return {"answer": response}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))