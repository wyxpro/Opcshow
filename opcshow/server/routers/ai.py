"""AI 服务域：内容创作、文案润色、知识答疑、简历优化、代码辅助。
当前为本地规则引擎演示实现；生产环境在 _call_llm() 中替换为大模型 API（OpenAI 兼容协议）。
"""
import re
import time

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatIn(BaseModel):
    message: str
    mode: str = "chat"  # create / polish / qa / resume / code / chat
    context: str = ""


def _call_llm(prompt: str, system: str = "") -> str | None:
    """对接大模型的统一入口（预留）：
    - 使用 OpenAI 兼容协议 POST {base_url}/chat/completions
    - 从环境变量 OPC_LLM_KEY / OPC_LLM_BASE / OPC_LLM_MODEL 读取配置
    未配置时返回 None，走本地规则引擎。
    """
    return None


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


def generate(mode: str, message: str) -> str:
    msg = message.strip()
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
                f"▸ 优化后：主导{msg[:30]}相关工作，通过量化手段拆解目标，"
                f"最终推动核心指标显著提升（建议补充具体数据，如「性能提升 40%」）。\n\n"
                f"▸ 建议：\n1. 每段经历以动词开头（主导/设计/落地）\n"
                f"2. 用数字替代形容词\n3. 与目标岗位 JD 关键词对齐")
    if mode == "qa":
        return (f"基于你的知识库，与「{msg}」最相关的内容：\n\n"
                f"1. 《组合式函数的设计哲学》— 前端开发 / Vue 生态\n"
                f"2. 《FastAPI 依赖注入实战》— 后端工程 / Python\n\n"
                f"要点总结：单一职责、显式依赖、可测试性是共同主题。"
                f"你可以在知识库中检索关键词进一步阅读。")
    if mode == "code":
        return (f"以下是「{msg}」的参考实现：\n\n"
                f"```ts\nfunction debounce<T extends (...args: any[]) => void>(fn: T, wait = 300) {{\n"
                f"  let timer: ReturnType<typeof setTimeout>\n"
                f"  return (...args: Parameters<T>) => {{\n    clearTimeout(timer)\n"
                f"    timer = setTimeout(() => fn(...args), wait)\n  }}\n}}\n```\n\n"
                f"说明：常用于搜索输入、窗口 resize 等高频事件降频。")
    # chat 兜底
    return (f"收到你的消息：「{msg[:60]}」。\n\n我是小舟助手，可以帮你：\n"
            f"▸ 创作：生成简介、随笔、朋友圈文案\n▸ 润色：让表达更专业\n"
            f"▸ 答疑：基于知识库回答\n▸ 简历：STAR 法则优化\n▸ 代码：给出示例实现\n\n"
            f"切换上方模式即可体验。")


@router.post("/chat")
def chat(body: ChatIn):
    t0 = time.time()
    llm = _call_llm(body.message)
    reply = llm if llm else generate(body.mode, body.message)
    return {"reply": reply, "mode": body.mode,
            "latency": round((time.time() - t0) * 1000), "engine": "llm" if llm else "local"}


@router.get("/capabilities")
def capabilities():
    return {"modes": [
        {"id": "chat", "name": "自由对话", "desc": "随便聊聊"},
        {"id": "create", "name": "内容创作", "desc": "简介/随笔/文案"},
        {"id": "polish", "name": "文案润色", "desc": "表达更专业"},
        {"id": "qa", "name": "知识答疑", "desc": "基于知识库"},
        {"id": "resume", "name": "简历优化", "desc": "STAR 法则"},
        {"id": "code", "name": "代码辅助", "desc": "示例与解释"},
    ]}
