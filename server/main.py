"""Opcshow API 服务入口。
启动：uvicorn main:app --host 0.0.0.0 --port 8000
接口统一前缀 /api，返回 JSON，错误使用 HTTPException(detail=...)。
"""
import time
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from db import init_db
from routers import admin, ai, core, fun, knowledge, life, social

app = FastAPI(title="Opcshow API", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 简易轻量级 IP 限流防护 (Rate Limiter) ----------
IP_REQUESTS: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_PATHS = {"/api/ai/chat", "/api/ai/stream", "/api/auth/login"}
MAX_REQUESTS_PER_MINUTE = 60


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if path in RATE_LIMIT_PATHS:
        client_ip = request.client.host if request.client else "127.0.0.1"
        now_ts = time.time()
        # 清理 60 秒前的历史记录
        IP_REQUESTS[client_ip] = [ts for ts in IP_REQUESTS[client_ip] if now_ts - ts < 60]

        if len(IP_REQUESTS[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试 (Rate limit exceeded)"}
            )
        IP_REQUESTS[client_ip].append(now_ts)

    response = await call_next(request)
    return response


app.include_router(core.router, prefix="/api", tags=["核心"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(life.router, prefix="/api/life", tags=["生活"])
app.include_router(fun.router, prefix="/api/fun", tags=["娱乐"])
app.include_router(social.router, prefix="/api/social", tags=["社交"])
app.include_router(admin.router, prefix="/api/admin", tags=["后台"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def on_error(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True, "service": "opcshow-api"}
