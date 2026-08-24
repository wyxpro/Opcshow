"""生活域：朋友圈动态、恋爱记录、旅拍点位、运动数据、游戏档案。"""
import json
from datetime import datetime

from fastapi import APIRouter, Header

from db import get_db, now, row, rows
from routers.core import require_admin

router = APIRouter()


def parse_json_fields(data, fields):
    for item in data:
        for f in fields:
            item[f] = json.loads(item.get(f) or "[]")
    return data


# ---------- 朋友圈 ----------
@router.get("/moments")
def list_moments():
    conn = get_db()
    data = parse_json_fields(rows(conn, "SELECT * FROM moments ORDER BY created_at DESC"), ["images"])
    conn.close()
    return data


@router.post("/moments")
def add_moment(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO moments(content,images,location,mood,likes,created_at) VALUES(?,?,?,?,0,?)",
        (body["content"], json.dumps(body.get("images", []), ensure_ascii=False),
         body.get("location", ""), body.get("mood", ""), now()))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.post("/moments/{mid}/like")
def like_moment(mid: int):
    conn = get_db()
    conn.execute("UPDATE moments SET likes=likes+1 WHERE id=?", (mid,))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.delete("/moments/{mid}")
def del_moment(mid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM moments WHERE id=?", (mid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 恋爱记录 ----------
@router.get("/love")
def love():
    conn = get_db()
    meta = row(conn, "SELECT * FROM love_meta WHERE id=1") or {}
    events = rows(conn, "SELECT * FROM love_events ORDER BY event_date DESC")
    conn.close()
    days = 0
    if meta.get("start_date"):
        days = (datetime.now() - datetime.strptime(meta["start_date"], "%Y-%m-%d")).days
    return {"meta": meta, "days": days, "events": events}


@router.post("/love/events")
def add_love_event(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO love_events(title,event_date,description,type,cover) VALUES(?,?,?,?,?)",
        (body["title"], body.get("event_date"), body.get("description", ""),
         body.get("type", "memory"), body.get("cover", "")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/love/events/{eid}")
def del_love_event(eid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM love_events WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 旅拍地图 ----------
@router.get("/travel")
def travel():
    conn = get_db()
    data = parse_json_fields(rows(conn, "SELECT * FROM travel_points ORDER BY visit_date DESC"), ["photos"])
    conn.close()
    return data


@router.post("/travel")
def add_travel(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO travel_points(name,x,y,region,visit_date,note,photos) VALUES(?,?,?,?,?,?,?)",
        (body["name"], body.get("x", 50), body.get("y", 50), body.get("region", ""),
         body.get("visit_date"), body.get("note", ""),
         json.dumps(body.get("photos", []), ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/travel/{tid}")
def del_travel(tid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM travel_points WHERE id=?", (tid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 运动数据 ----------
@router.get("/sports")
def sports():
    conn = get_db()
    data = rows(conn, "SELECT * FROM sports ORDER BY sport_date DESC LIMIT 60")
    conn.close()
    stats = {}
    for s in data:
        t = s["type"]
        stats.setdefault(t, {"count": 0, "total": 0.0})
        stats[t]["count"] += 1
        stats[t]["total"] += s["value"]
    return {"list": data, "stats": stats}


@router.post("/sports")
def add_sport(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO sports(type,sport_date,value,unit,duration,note) VALUES(?,?,?,?,?,?)",
        (body["type"], body.get("sport_date"), body.get("value", 0),
         body.get("unit", "km"), body.get("duration", 0), body.get("note", "")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/sports/{sid}")
def del_sport(sid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM sports WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 游戏档案 ----------
@router.get("/games")
def games():
    conn = get_db()
    data = rows(conn, "SELECT * FROM games ORDER BY hours DESC")
    conn.close()
    return data


@router.post("/games")
def add_game(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO games(name,platform,role,level,hours,achievement,cover) VALUES(?,?,?,?,?,?,?)",
        (body["name"], body.get("platform", ""), body.get("role", ""), body.get("level", ""),
         body.get("hours", 0), body.get("achievement", ""), body.get("cover", "")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/games/{gid}")
def del_game(gid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM games WHERE id=?", (gid,))
    conn.commit()
    conn.close()
    return {"ok": True}
