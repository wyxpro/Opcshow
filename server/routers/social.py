"""社交域：友链、留言弹幕（AI 审核）、成长时间轴、自媒体矩阵、分享。"""
import random
import re

from fastapi import APIRouter, Header, HTTPException

from db import get_db, now, rows
from routers.core import require_admin

router = APIRouter()

# 简易内容风控词库（PRD：留言智能审核）
BANNED = ["发票", "代开", "加微信", "赌博", "刷单", "广告联系"]
DANMAKU_COLORS = ["#E4572E", "#3D7A5E", "#E8A13C", "#2E86AB", "#D4577A", "#5B8C5A", "#8A5CF6"]


def audit_content(text: str) -> bool:
    return not any(w in text for w in BANNED)


# ---------- 友链 ----------
@router.get("/links")
def list_links(all: bool = False):
    conn = get_db()
    if all:
        data = rows(conn, "SELECT * FROM friend_links ORDER BY created_at DESC")
    else:
        data = rows(conn, "SELECT * FROM friend_links WHERE status='approved' ORDER BY created_at DESC")
    conn.close()
    return data


@router.post("/links")
def apply_link(body: dict):
    """访客申请友链，待审核。"""
    if not body.get("name") or not body.get("url"):
        raise HTTPException(400, "名称与链接必填")
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO friend_links(name,url,avatar,description,status,created_at) VALUES(?,?,?,?,'pending',?)",
        (body["name"], body["url"], body.get("avatar", ""), body.get("description", ""), now()))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid, "status": "pending"}


@router.put("/links/{lid}")
def review_link(lid: int, body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("UPDATE friend_links SET status=? WHERE id=?", (body.get("status", "approved"), lid))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.delete("/links/{lid}")
def del_link(lid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM friend_links WHERE id=?", (lid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 留言弹幕 ----------
@router.get("/messages")
def list_messages(all: bool = False):
    conn = get_db()
    if all:
        data = rows(conn, "SELECT * FROM messages ORDER BY pinned DESC, created_at DESC LIMIT 100")
    else:
        data = rows(conn,
                    "SELECT * FROM messages WHERE status='approved' ORDER BY pinned DESC, created_at DESC LIMIT 100")
    conn.close()
    return data


@router.post("/messages")
def add_message(body: dict):
    """访客留言：AI 风控审核，合规直接展示，违规进入待审。"""
    nickname = (body.get("nickname") or "匿名访客").strip()[:20]
    content = (body.get("content") or "").strip()
    if not content:
        raise HTTPException(400, "留言内容不能为空")
    if len(content) > 120:
        raise HTTPException(400, "留言最多 120 字")
    passed = audit_content(content)
    status = "approved" if passed else "pending"
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO messages(nickname,content,color,likes,pinned,reply,status,created_at) VALUES(?,?,?,0,0,'',?,?)",
        (nickname, content, body.get("color") or random.choice(DANMAKU_COLORS), status, now()))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid, "status": status,
            "audit": "passed" if passed else "blocked",
            "tip": "留言已上墙" if passed else "留言进入审核队列，通过后展示"}


@router.post("/messages/{mid}/like")
def like_message(mid: int):
    conn = get_db()
    conn.execute("UPDATE messages SET likes=likes+1 WHERE id=?", (mid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 成长时间轴 ----------
@router.get("/timeline")
def list_timeline():
    conn = get_db()
    data = rows(conn, "SELECT * FROM timeline ORDER BY event_date DESC")
    conn.close()
    return data


@router.post("/timeline")
def add_timeline(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO timeline(event_date,title,description,tag) VALUES(?,?,?,?)",
        (body["event_date"], body["title"], body.get("description", ""), body.get("tag", "成长")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/timeline/{tid}")
def del_timeline(tid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM timeline WHERE id=?", (tid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 自媒体矩阵 ----------
@router.get("/accounts")
def list_accounts():
    conn = get_db()
    data = rows(conn, "SELECT * FROM social_accounts ORDER BY id")
    conn.close()
    return data


@router.post("/accounts")
def add_account(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO social_accounts(platform,handle,url,followers,icon,description) VALUES(?,?,?,?,?,?)",
        (body["platform"], body.get("handle", ""), body.get("url", ""),
         body.get("followers", "0"), body.get("icon", "◈"), body.get("description", "")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/accounts/{aid}")
def del_account(aid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM social_accounts WHERE id=?", (aid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 分享 ----------
@router.get("/share/{target}")
def share(target: str):
    """生成分享卡片所需的元信息（前端 Canvas 渲染）。"""
    conn = get_db()
    p = None
    if target == "home":
        p = rows(conn, "SELECT name,title,bio FROM profile WHERE id=1")
    title, desc = "Opcshow · 林一舟的个人主页", "一个聚合展示、记录与社交的数字自留地"
    if p:
        title = f"{p[0]['name']} · {p[0]['title']}"
        desc = (p[0]["bio"] or "")[:40]
    conn.close()
    import hashlib, time
    short = hashlib.md5(f"{target}{time.time()}".encode()).hexdigest()[:6]
    return {"title": title, "desc": desc, "shortCode": short,
            "url": f"https://opcshow.cn/s/{short}", "target": target}
