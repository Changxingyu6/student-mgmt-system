"""
AI 服务模块
集成火山引擎方舟 DeepSeek 模型 API
"""
import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
SERVICE_DIR = Path(__file__).resolve().parent
load_dotenv(SERVICE_DIR.parent / ".env")


def chat_with_ai_stream(messages: list):
    """
    与AI对话（流式响应生成器）
    
    Args:
        messages: 消息列表，格式: [{"role": "user", "content": "..."}]
    
    Yields:
        SSE 格式的文本片段
    """
    # 从环境变量读取配置
    base_url = os.environ.get("ARK_BASE_URL")
    api_key = os.environ.get("ARK_API_KEY")
    model = os.environ.get("ARK_MODEL")
    
    # 转换消息格式
    input_content = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "user":
            input_content.append({
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": content
                }]
            })
        elif role == "assistant":
            input_content.append({
                "role": "assistant",
                "content": [{
                    "type": "output_text",
                    "text": content
                }]
            })
    
    # 构建请求
    url = f"{base_url}/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "stream": True,
        "input": input_content
    }
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        
        # 处理流式响应
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                # 解析 SSE 格式
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 移除 'data: ' 前缀
                    try:
                        data = json.loads(data_str)
                        
                        # 提取文本内容
                        # 1. reasoning_summary_text.delta - 思考过程
                        if data.get('type') == 'response.reasoning_summary_text.delta':
                            delta = data.get('delta', '')
                            if delta:
                                yield f"data: {json.dumps({'type': 'text', 'content': delta})}\n\n"
                        
                        # 2. output_text.delta - 实际输出文本
                        elif data.get('type') == 'response.output_text.delta':
                            delta = data.get('delta', '')
                            if delta:
                                yield f"data: {json.dumps({'type': 'text', 'content': delta})}\n\n"
                        
                        # 3. response.completed - 完成
                        elif data.get('type') == 'response.completed':
                            yield f"data: {json.dumps({'type': 'done'})}\n\n"
                            
                    except json.JSONDecodeError:
                        continue
                        
        # 响应结束时发送完成信号
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        # 发生错误时发送错误信号
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


def chat_with_ai(
    messages: list, 
    model: str = None,
    stream: bool = None
):
    """
    与AI对话（非流式响应）
    
    Args:
        messages: 消息列表，格式: [{"role": "user", "content": "..."}]
        model: 模型名称/接入点ID
        stream: 是否流式响应
    
    Returns:
        响应内容
    """
    # 从环境变量读取配置
    base_url = os.environ.get("ARK_BASE_URL")
    api_key = os.environ.get("ARK_API_KEY")
    default_model = os.environ.get("ARK_MODEL")
    default_stream = os.environ.get("ARK_STREAM", "false").lower() == "true"
    
    # 使用传入的值或默认值
    model = model or default_model
    stream = stream if stream is not None else default_stream
    
    # 转换消息格式
    input_content = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "user":
            input_content.append({
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": content
                }]
            })
        elif role == "assistant":
            input_content.append({
                "role": "assistant",
                "content": [{
                    "type": "output_text",
                    "text": content
                }]
            })
    
    # 构建请求
    url = f"{base_url}/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "stream": stream,
        "input": input_content
    }
    
    # 发送请求
    response = requests.post(url, headers=headers, json=payload, stream=stream)
    response.raise_for_status()
    
    if stream:
        # 流式响应处理
        return response.iter_lines()
    else:
        # 非流式响应处理
        result = response.json()
        return {
            "content": result.get("output", [{}])[0].get("content", [{}])[0].get("text", ""),
            "reasoning": None
        }