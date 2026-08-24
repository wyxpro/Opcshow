"""后台管理域：数据统计、留言审核、内容概览。"""
from fastapi import APIRouter, Header, HTTPException

from db import get_db, rows
from routers.core import require_admin

router = APIRouter()


@router.get("/stats")
def stats(authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    counts = {}
    for table, label in [("kb_articles", "articles"), ("projects", "projects"),
                         ("moments", "moments"), ("messages", "messages"),
                         ("travel_points", "travel"), ("movies", "movies"),
                         ("music", "music"), ("friend_links", "links")]:
        counts[label] = conn.execute(f"SELECT COUNT(*) c FROM {table}").fetchone()["c"]
    visits = rows(conn, "SELECT visit_date, count FROM visits ORDER BY visit_date DESC LIMIT 30")
    visits.reverse()
    total_visits = sum(v["count"] for v in visits)
    pending_msgs = conn.execute("SELECT COUNT(*) c FROM messages WHERE status='pending'").fetchone()["c"]
    pending_links = conn.execute("SELECT COUNT(*) c FROM friend_links WHERE status='pending'").fetchone()["c"]
    conn.close()
    return {"counts": counts, "visits": visits, "totalVisits": total_visits,
            "pending": {"messages": pending_msgs, "links": pending_links}}


@router.post("/messages/{mid}/review")
def review_message(mid: int, body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    action = body.get("action")  # approve / reject / pin / reply / delete
    conn = get_db()
    if action == "approve":
        conn.execute("UPDATE messages SET status='approved' WHERE id=?", (mid,))
    elif action == "reject":
        conn.execute("UPDATE messages SET status='rejected' WHERE id=?", (mid,))
    elif action == "pin":
        conn.execute("UPDATE messages SET pinned=1-pinned WHERE id=?", (mid,))
    elif action == "reply":
        conn.execute("UPDATE messages SET reply=? WHERE id=?", (body.get("reply", ""), mid))
    elif action == "delete":
        conn.execute("DELETE FROM messages WHERE id=?", (mid,))
    else:
        conn.close()
        raise HTTPException(400, "未知操作")
    conn.commit()
    conn.close()
    return {"ok": True}
