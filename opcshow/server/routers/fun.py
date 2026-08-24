"""娱乐域：音乐盒、电影收藏、百宝箱收藏夹。"""
from fastapi import APIRouter, Header

from db import get_db, rows
from routers.core import require_admin

router = APIRouter()


# ---------- 音乐盒 ----------
@router.get("/music")
def list_music():
    conn = get_db()
    data = rows(conn, "SELECT * FROM music ORDER BY liked DESC, id")
    conn.close()
    return data


@router.post("/music")
def add_music(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO music(title,artist,album,url,cover,duration,liked) VALUES(?,?,?,?,?,?,0)",
        (body["title"], body.get("artist", ""), body.get("album", ""),
         body["url"], body.get("cover", ""), body.get("duration", 0)))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.post("/music/{mid}/like")
def like_music(mid: int):
    conn = get_db()
    conn.execute("UPDATE music SET liked=1-liked WHERE id=?", (mid,))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.delete("/music/{mid}")
def del_music(mid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM music WHERE id=?", (mid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 电影收藏 ----------
@router.get("/movies")
def list_movies(category: str = "", status: str = ""):
    conn = get_db()
    sql, params = "SELECT * FROM movies WHERE 1=1", []
    if category:
        sql += " AND category=?"
        params.append(category)
    if status:
        sql += " AND status=?"
        params.append(status)
    sql += " ORDER BY rating DESC"
    data = rows(conn, sql, params)
    cats = [r["category"] for r in rows(conn, "SELECT DISTINCT category FROM movies")]
    conn.close()
    return {"list": data, "categories": cats}


@router.post("/movies")
def add_movie(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO movies(title,category,rating,year,poster,comment,status,director) VALUES(?,?,?,?,?,?,?,?)",
        (body["title"], body.get("category", "剧情"), body.get("rating", 8.0),
         body.get("year", 2024), body.get("poster", ""), body.get("comment", ""),
         body.get("status", "已看"), body.get("director", "")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/movies/{mid}")
def del_movie(mid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM movies WHERE id=?", (mid,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 百宝箱 ----------
@router.get("/box")
def box():
    conn = get_db()
    cats = rows(conn, "SELECT * FROM box_categories ORDER BY sort,id")
    items = rows(conn, "SELECT * FROM box_items ORDER BY id")
    conn.close()
    for c in cats:
        c["items"] = [i for i in items if i["category_id"] == c["id"]]
    return cats


@router.post("/box/categories")
def add_box_cat(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute("INSERT INTO box_categories(name,icon,sort) VALUES(?,?,99)",
                       (body["name"], body.get("icon", "✦")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.post("/box/items")
def add_box_item(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO box_items(category_id,title,url,description) VALUES(?,?,?,?)",
        (body["category_id"], body["title"], body.get("url", ""), body.get("description", "")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/box/items/{iid}")
def del_box_item(iid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM box_items WHERE id=?", (iid,))
    conn.commit()
    conn.close()
    return {"ok": True}
