"""知识库域：三级目录 + 文章 CRUD + 检索。"""
import json

from fastapi import APIRouter, Header, HTTPException, Query

from db import get_db, now, row, rows
from routers.core import require_admin

router = APIRouter()


def build_tree(cats):
    by_id = {c["id"]: {**c, "children": []} for c in cats}
    roots = []
    for c in by_id.values():
        if c["parent_id"] and c["parent_id"] in by_id:
            by_id[c["parent_id"]]["children"].append(c)
        else:
            roots.append(c)
    return roots


@router.get("/categories")
def categories():
    conn = get_db()
    cats = rows(conn, "SELECT * FROM kb_categories ORDER BY sort,id")
    counts = {r["category_id"]: r["c"] for r in
              rows(conn, "SELECT category_id, COUNT(*) c FROM kb_articles GROUP BY category_id")}
    conn.close()
    for c in cats:
        c["article_count"] = counts.get(c["id"], 0)
    return build_tree(cats)


@router.post("/categories")
def add_category(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    parent = body.get("parent_id", 0)
    level = 1
    conn = get_db()
    if parent:
        p = row(conn, "SELECT level FROM kb_categories WHERE id=?", (parent,))
        if not p:
            raise HTTPException(404, "父目录不存在")
        level = p["level"] + 1
        if level > 3:
            conn.close()
            raise HTTPException(400, "最多支持三级目录")
    cur = conn.execute(
        "INSERT INTO kb_categories(name,parent_id,level,sort) VALUES(?,?,?,?)",
        (body["name"], parent, level, body.get("sort", 99)))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid, "level": level}


@router.delete("/categories/{cid}")
def del_category(cid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    child = row(conn, "SELECT id FROM kb_categories WHERE parent_id=? LIMIT 1", (cid,))
    art = row(conn, "SELECT id FROM kb_articles WHERE category_id=? LIMIT 1", (cid,))
    if child or art:
        conn.close()
        raise HTTPException(400, "目录下存在子目录或文章，无法删除")
    conn.execute("DELETE FROM kb_categories WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.get("/articles")
def articles(category_id: int | None = None, keyword: str = "",
             page: int = 1, size: int = 10):
    conn = get_db()
    sql, params = "SELECT id,category_id,title,summary,tags,views,created_at,updated_at FROM kb_articles", []
    where = []
    if category_id:
        # 包含子孙目录的文章
        ids = {category_id}
        frontier = [category_id]
        while frontier:
            found = rows(conn, f"SELECT id FROM kb_categories WHERE parent_id IN ({','.join('?'*len(frontier))})", frontier)
            frontier = [f["id"] for f in found]
            ids.update(frontier)
        where.append(f"category_id IN ({','.join(str(i) for i in ids)})")
    if keyword:
        where.append("(title LIKE ? OR summary LIKE ? OR content LIKE ?)")
        kw = f"%{keyword}%"
        params += [kw, kw, kw]
    if where:
        sql += " WHERE " + " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) c FROM ({sql})", params).fetchone()["c"]
    sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
    data = rows(conn, sql, params + [size, (page - 1) * size])
    conn.close()
    for a in data:
        a["tags"] = json.loads(a.get("tags") or "[]")
    return {"list": data, "total": total, "page": page, "size": size}


@router.get("/articles/{aid}")
def article_detail(aid: int):
    conn = get_db()
    a = row(conn, "SELECT * FROM kb_articles WHERE id=?", (aid,))
    if not a:
        conn.close()
        raise HTTPException(404, "文章不存在")
    conn.execute("UPDATE kb_articles SET views=views+1 WHERE id=?", (aid,))
    conn.commit()
    conn.close()
    a["tags"] = json.loads(a.get("tags") or "[]")
    return a


@router.post("/articles")
def add_article(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO kb_articles(category_id,title,summary,content,tags,views,created_at,updated_at)
        VALUES(?,?,?,?,?,0,?,?)""",
        (body.get("category_id"), body["title"], body.get("summary", ""),
         body.get("content", ""), json.dumps(body.get("tags", []), ensure_ascii=False),
         now(), now()))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.put("/articles/{aid}")
def update_article(aid: int, body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute(
        "UPDATE kb_articles SET category_id=?,title=?,summary=?,content=?,tags=?,updated_at=? WHERE id=?",
        (body.get("category_id"), body.get("title"), body.get("summary", ""),
         body.get("content", ""), json.dumps(body.get("tags", []), ensure_ascii=False), now(), aid))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.delete("/articles/{aid}")
def del_article(aid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM kb_articles WHERE id=?", (aid,))
    conn.commit()
    conn.close()
    return {"ok": True}
