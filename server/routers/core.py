"""核心域：登录鉴权、个人资料、技能、作品、兴趣、布局、系统设置、简历。"""
import json

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from db import get_db, now, row, rows

router = APIRouter()

TOKENS = {"demo-token-admin": {"user": "admin", "role": "admin"}}


def require_admin(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "未登录")
    token = authorization.removeprefix("Bearer ")
    if token not in TOKENS:
        raise HTTPException(401, "登录已失效")
    return TOKENS[token]


class LoginIn(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def login(body: LoginIn):
    conn = get_db()
    u = row(conn, "SELECT * FROM users WHERE username=? AND password=?",
            (body.username, body.password))
    conn.close()
    if not u:
        raise HTTPException(401, "账号或密码错误")
    TOKENS["demo-token-admin"] = {"user": u["username"], "role": u["role"]}
    return {"token": "demo-token-admin",
            "user": {"username": u["username"], "nickname": u["nickname"], "role": u["role"]}}


@router.get("/auth/me")
def me(authorization: str | None = Header(None)):
    return {"user": require_admin(authorization)}


# ---------- 个人资料 / 技能 / 作品 / 兴趣 ----------

@router.get("/profile")
def get_profile():
    conn = get_db()
    p = row(conn, "SELECT * FROM profile WHERE id=1")
    conn.close()
    if p:
        p["tags"] = json.loads(p.get("tags") or "[]")
        p["socials"] = json.loads(p.get("socials") or "{}")
    return p


@router.put("/profile")
def update_profile(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    fields = ["name", "title", "bio", "location", "motto", "email", "avatar"]
    sets, params = [], []
    for f in fields:
        if f in body:
            sets.append(f"{f}=?")
            params.append(body[f])
    if "tags" in body:
        sets.append("tags=?")
        params.append(json.dumps(body["tags"], ensure_ascii=False))
    if "socials" in body:
        sets.append("socials=?")
        params.append(json.dumps(body["socials"], ensure_ascii=False))
    if not sets:
        return get_profile()
    sets.append("updated_at=?")
    params.append(now())
    conn = get_db()
    conn.execute(f"UPDATE profile SET {','.join(sets)} WHERE id=1", params)
    conn.commit()
    conn.close()
    return get_profile()


@router.get("/skills")
def list_skills():
    conn = get_db()
    data = rows(conn, "SELECT * FROM skills ORDER BY level DESC")
    conn.close()
    return data


@router.post("/skills")
def add_skill(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute("INSERT INTO skills(name,level,category) VALUES(?,?,?)",
                       (body["name"], body.get("level", 60), body.get("category", "技术")))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.delete("/skills/{sid}")
def del_skill(sid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM skills WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.get("/projects")
def list_projects():
    conn = get_db()
    data = rows(conn, "SELECT * FROM projects ORDER BY sort, id")
    conn.close()
    for p in data:
        p["tags"] = json.loads(p.get("tags") or "[]")
    return data


@router.post("/projects")
def add_project(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO projects(title,description,cover,link,tags,featured,sort) VALUES(?,?,?,?,?,?,?)",
        (body["title"], body.get("description", ""), body.get("cover", ""),
         body.get("link", ""), json.dumps(body.get("tags", []), ensure_ascii=False),
         body.get("featured", 0), body.get("sort", 99)))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.put("/projects/{pid}")
def update_project(pid: int, body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute(
        "UPDATE projects SET title=?,description=?,cover=?,link=?,tags=?,featured=? WHERE id=?",
        (body.get("title"), body.get("description", ""), body.get("cover", ""),
         body.get("link", ""), json.dumps(body.get("tags", []), ensure_ascii=False),
         body.get("featured", 0), pid))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.delete("/projects/{pid}")
def del_project(pid: int, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.get("/interests")
def list_interests():
    conn = get_db()
    data = rows(conn, "SELECT * FROM interests ORDER BY id")
    conn.close()
    return data


# ---------- 布局（拖拽自定义） ----------

@router.get("/layout")
def get_layout():
    conn = get_db()
    l = row(conn, "SELECT * FROM layouts WHERE active=1 ORDER BY id LIMIT 1")
    conn.close()
    if l:
        l["config"] = json.loads(l["config"])
    return l


@router.put("/layout")
def save_layout(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    active = row(conn, "SELECT id FROM layouts WHERE active=1")
    config = json.dumps(body.get("config", []), ensure_ascii=False)
    if active:
        conn.execute("UPDATE layouts SET config=?,updated_at=? WHERE id=?", (config, now(), active["id"]))
    else:
        conn.execute("INSERT INTO layouts(name,config,active,updated_at) VALUES('默认布局',?,1,?)",
                     (config, now()))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 简历 ----------

@router.get("/resume")
def get_resume():
    conn = get_db()
    r = row(conn, "SELECT * FROM resumes ORDER BY id LIMIT 1")
    conn.close()
    if r:
        r["data"] = json.loads(r["data"])
    return r


@router.put("/resume")
def save_resume(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    r = row(conn, "SELECT id FROM resumes ORDER BY id LIMIT 1")
    data = json.dumps(body.get("data", {}), ensure_ascii=False)
    if r:
        conn.execute("UPDATE resumes SET name=?,template=?,data=?,updated_at=? WHERE id=?",
                     (body.get("name", "我的简历"), body.get("template", "minimal"), data, now(), r["id"]))
    else:
        conn.execute("INSERT INTO resumes(name,template,data,updated_at) VALUES(?,?,?,?)",
                     (body.get("name", "我的简历"), body.get("template", "minimal"), data, now()))
    conn.commit()
    conn.close()
    return {"ok": True}


# ---------- 设置 ----------

@router.get("/settings")
def get_settings():
    conn = get_db()
    data = {r["key"]: json.loads(r["value"]) for r in rows(conn, "SELECT * FROM settings")}
    conn.close()
    return data


@router.put("/settings/{key}")
def put_setting(key: str, body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute(
        "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, json.dumps(body.get("value"), ensure_ascii=False)))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.post("/visit")
def track_visit():
    """记录访问（管理端统计用）。"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    conn.execute(
        "INSERT INTO visits(visit_date,count) VALUES(?,1) "
        "ON CONFLICT(visit_date) DO UPDATE SET count=count+1", (today,))
    conn.commit()
    conn.close()
    return {"ok": True}
