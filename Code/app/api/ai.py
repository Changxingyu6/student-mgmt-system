"""
AI 对话路由
提供与AI交互的API接口
"""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List
from services.ai_service import chat_with_ai_stream

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
async def chat(request: Request, chat_request: ChatRequest):
    """AI对话接口（流式响应）- 所有登录用户可用"""
    # 将消息转换为API格式
    messages = [{"role": m.role, "content": m.content} for m in chat_request.messages]
    
    # 返回流式响应
    return StreamingResponse(
        chat_with_ai_stream(messages),
        media_type="text/event-stream"
    )