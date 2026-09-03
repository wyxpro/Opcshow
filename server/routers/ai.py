"""AI 服务域：内容创作、文案润色、知识答疑、简历优化、代码辅助。
支持真实接入 OpenAI 兼容 REST 大模型 API、SSE (Server-Sent Events) 流式打字机响应、RAG 知识库检索与多轮会话上下文。
"""
import asyncio
import json
import os
import re
import time
from typing import Any, AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from db import get_db

router = APIRouter()


class ChatIn(BaseModel):
    message: str
    mode: str = "chat"  # create / polish / qa / resume / code / chat
    context: str = ""
    history: list[dict[str, str]] = []  # 多轮对话历史 [{"role": "user"|"assistant", "content": "..."}]


def polish_text(text: str) -> str:
    t = re.sub(r"\s+", " ", text.strip())
    upgrades = [
        ("很好", "出色"), ("很多", "大量"), ("负责了", "主导"), ("做了", "落地了"),
        ("提升很大", "显著提升"), ("帮忙", "协同"), ("写了", "设计并实现了"),
    ]
    for old, new in upgrades:
        t = t.replace(old, new)
    if not t.endswith(("。", "！", "？", ".", "!", "?")):
        t += "。"
    return t


def search_kb_rag(query: str) -> str:
    """在 SQLite 中基于关键词匹配 `kb_articles` 表做轻量 RAG 知识库检索增强"""
    if not query.strip():
        return ""
    keywords = [k for k in re.split(r"[\s,，.准？?]+", query) if len(k) >= 2]
    if not keywords:
        return ""
    try:
        conn = get_db()
        conditions = []
        params = []
        for k in keywords[:3]:
            conditions.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f"%{k}%", f"%{k}%"])
        sql = f"SELECT title, summary, content FROM kb_articles WHERE {' OR '.join(conditions)} LIMIT 2"
        results = conn.execute(sql, params).fetchall()
        conn.close()
        if not results:
            return ""
        excerpts = []
        for r in results:
            excerpts.append(f"【文章】《{r['title']}》\n摘要：{r['summary']}\n内容片段：{r['content'][:250]}...")
        return "\n\n[系统自动检索到的知识库背景内容]\n" + "\n---\n".join(excerpts)
    except Exception:
        return ""


def generate(mode: str, message: str) -> str:
    msg = message.strip()
    rag_ctx = search_kb_rag(msg) if mode == "qa" else ""

    if mode == "create":
        topic = msg or "今天的日常"
        return (f"关于「{topic}」，为你准备了两个版本：\n\n"
                f"【文艺版】\n{topic}——把平凡的日子过成值得收藏的一页。"
                f"光线、气味与心情在此刻对齐，记录本身就是意义。\n\n"
                f"【简洁版】\n{topic}。认真经历，如实记录。")
    if mode == "polish":
        return f"润色结果：\n\n{polish_text(msg)}\n\n主要调整：精简冗余表达、强化动词、统一语气。"
    if mode == "resume":
        return (f"已按「STAR 法则」优化你的描述：\n\n"
                f"▸ 原表述：{msg[:50]}{'…' if len(msg) > 50 else ''}\n\n"
                f"▸ 优化后：主导 {msg[:30]} 相关工作，通过量化手段拆解目标，"
                f"最终推动核心指标显著提升（建议补充具体数据，如「性能提升 40%」）。\n\n"
                f"▸ 建议：\n1. 每段经历以动词开头（主导/设计/落地）\n"
                f"2. 用数字替代形容词\n3. 与目标岗位 JD 关键词对齐")
    if mode == "qa":
        prefix = f"已完成知识库 RAG 全文检索。\n\n{rag_ctx}\n\n" if rag_ctx else ""
        return (f"{prefix}基于你的知识库，与「{msg}」最相关的内容总结如下：\n\n"
                f"1. 《组合式函数的设计哲学》— 前端开发 / Vue 生态\n"
                f"2. 《FastAPI 依赖注入实战》— 后端工程 / Python\n\n"
                f"要点总结：单一职责、显式依赖、可测试性是共同主题。你可以直接在知识库检索关键词进一步阅读。")
    if mode == "code":
        return (f"以下是「{msg}」的参考实现：\n\n"
                f"```ts\nfunction debounce<T extends (...args: any[]) => void>(fn: T, wait = 300) {{\n"
                f"  let timer: ReturnType<typeof setTimeout>\n"
                f"  return (...args: Parameters<T>) => {{\n    clearTimeout(timer)\n"
                f"    timer = setTimeout(() => fn(...args), wait)\n  }}\n}}\n```\n\n"
                f"说明：常用于搜索输入、窗口 resize 等高频事件降频。")

    return (f"收到你的消息：「{msg[:60]}」。\n\n我是小舟助手，可以帮你：\n"
            f"▸ 创作：生成简介、随笔、朋友圈文案\n▸ 润色：让表达更专业\n"
            f"▸ 答疑：基于知识库回答 (RAG 检索)\n▸ 简历：STAR 法则优化\n▸ 代码：给出示例实现\n\n"
            f"切换上方模式即可体验。")


async def _call_llm_stream(prompt: str, mode: str = "chat", history: list[dict[str, str]] = None) -> AsyncGenerator[str, None]:
    """真实 LLM / 本地降级 SSE 流式生成器 (支持多轮对话 & RAG 知识库检索)"""
    api_key = os.environ.get("OPC_LLM_KEY")
    api_base = os.environ.get("OPC_LLM_BASE", "https://api.deepseek.com/v1").rstrip("/")
    api_model = os.environ.get("OPC_LLM_MODEL", "deepseek-chat")

    system_prompt = "你是小舟助手，一位精通技术与创作的智能个人助理。"
    if mode == "polish":
        system_prompt = "你是专业的文案润色大师，精简冗余表达，强化动词，统一专业语气。"
    elif mode == "resume":
        system_prompt = "你是资深 HR 与职业顾问，使用 STAR 法则结构化优化简历描述。"
    elif mode == "code":
        system_prompt = "你是资深全栈工程师，提供清晰带注释的高质量代码与解释。"
    elif mode == "qa":
        system_prompt = "你是知识库智能解答专家，参考给出的知识库文章背景材料精准回答用户问题。"

    # 如果是知识答疑，自动检索知识库做 RAG
    rag_info = search_kb_rag(prompt) if mode == "qa" else ""
    user_content = prompt + (f"\n\n{rag_info}" if rag_info else "")

    if api_key:
        try:
            import httpx
            messages = [{"role": "system", "content": system_prompt}]
            # 引入历史多轮会话
            if history:
                for h in history[-6:]:  # 最多保留近 6 条上下文
                    messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            messages.append({"role": "user", "content": user_content})

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.send(
                    client.build_request(
                        "POST",
                        f"{api_base}/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={
                            "model": api_model,
                            "messages": messages,
                            "stream": True,
                            "temperature": 0.7,
                        }
                    ),
                    stream=True
                )
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line.removeprefix("data: ").strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            payload = json.loads(data_str)
                            chunk = payload.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if chunk:
                                yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
                        except Exception:
                            continue
            yield "data: [DONE]\n\n"
            return
        except Exception as e:
            yield f"data: {json.dumps({'text': f'\\n\\n*(大模型调用异常: {str(e)}，已降级为规则引擎响应)*\\n\\n'}, ensure_ascii=False)}\n\n"

    # 本地规则引擎降级打字机推流
    full_text = generate(mode, prompt)
    step = 2
    for i in range(0, len(full_text), step):
        chunk = full_text[i:i + step]
        yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.015)

    yield "data: [DONE]\n\n"


@router.post("/chat")
def chat(body: ChatIn):
    t0 = time.time()
    reply = generate(body.mode, body.message)
    return {
        "reply": reply,
        "mode": body.mode,
        "latency": round((time.time() - t0) * 1000),
        "engine": "local"
    }


@router.post("/stream")
async def chat_stream(body: ChatIn):
    """SSE 流式 AI 聊天响应接口 (支持多轮对话与 RAG)"""
    return StreamingResponse(
        _call_llm_stream(body.message, body.mode, body.history),
        media_type="text/event-stream"
    )


@router.get("/capabilities")
def capabilities():
    return {"modes": [
        {"id": "chat", "name": "自由对话", "desc": "随便聊聊"},
        {"id": "create", "name": "内容创作", "desc": "简介/随笔/文案"},
        {"id": "polish", "name": "文案润色", "desc": "表达更专业"},
        {"id": "qa", "name": "知识答疑", "desc": "基于知识库 (RAG)"},
        {"id": "resume", "name": "简历优化", "desc": "STAR 法则"},
        {"id": "code", "name": "代码辅助", "desc": "示例与解释"},
    ]}
