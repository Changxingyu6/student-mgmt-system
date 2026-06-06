"""
AI 对话路由
提供与AI交互的API接口
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from services.ai_service import chat_with_ai_stream
from deps import get_current_user

router = APIRouter(
    prefix="/ai",
    tags=["AI对话"]
)


class ChatMessage(BaseModel):
    role: str = Field(..., description="角色：user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="消息历史")


@router.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """AI对话接口（流式响应）"""
    # 将消息转换为API格式
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    # 返回流式响应
    return StreamingResponse(
        chat_with_ai_stream(messages),
        media_type="text/event-stream"
    )