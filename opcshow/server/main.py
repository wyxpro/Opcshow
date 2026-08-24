"""Opcshow API 服务入口。
启动：uvicorn main:app --host 0.0.0.0 --port 8000
接口统一前缀 /api，返回 JSON，错误使用 HTTPException(detail=...)。
"""
from fastapi import FastAPI, Request
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

app.include_router(core.router, prefix="/api", tags=["核心"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(life.router, prefix="/api/life", tags=["生活"])
app.include_router(fun.router, prefix="/api/fun", tags=["娱乐"])
app.include_router(social.router, prefix="/api/social", tags=["社交"])
app.include_router(admin.router, prefix="/api/admin", tags=["后台"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])


@app.exception_handler(Exception)
async def on_error(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True, "service": "opcshow-api"}
