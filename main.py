from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()
client = httpx.AsyncClient()

# 从环境变量读取配置
UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://api.deepinfra.com/v1")
UPSTREAM_KEY = os.getenv("UPSTREAM_KEY", "你从DeepInfra复制的那串密钥")
YOUR_API_KEY = os.getenv("YOUR_API_KEY", "自己设一个复杂的密码")

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    # 1. 验证是否是 OpenRouter 发来的请求
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {YOUR_API_KEY}":
        return {"error": "Unauthorized"}, 401

    # 2. 接收请求体
    body = await request.json()

    # 3. 转发给上游 DeepInfra
    headers = {
        "Authorization": f"Bearer {UPSTREAM_KEY}",
        "Content-Type": "application/json"
    }
    
    # 对模型名做简单处理，去除可能的前缀
    if "/" in body.get("model", ""):
        body["model"] = body["model"].split("/")[-1]

    # 4. 将上游的响应直接返回
    resp = await client.post(f"{UPSTREAM_URL}/chat/completions", json=body, headers=headers)
    return resp.json()

@app.get("/v1/models")
async def list_models():
    headers = {"Authorization": f"Bearer {UPSTREAM_KEY}"}
    resp = await client.get(f"{UPSTREAM_URL}/models", headers=headers)
    return resp.json()
