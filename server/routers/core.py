"""核心域：登录鉴权、个人资料、技能、作品、兴趣、布局、系统设置、简历。"""
import json
import time
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from db import get_db, now, row, rows

router = APIRouter()

SECRET_KEY = "opcshow_jwt_secret_key_2026_prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 86400 * 7  # 7 days


def create_access_token(data: dict) -> str:
    """签发 JWT Token"""
    try:
        import jwt
        to_encode = data.copy()
        to_encode.update({"exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception:
        # Fallback if pyjwt has any environment issue
        return f"demo-token-{data.get('user', 'admin')}"


def require_admin(authorization: str | None) -> dict:
    """JWT 权限守卫拦截器"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "未登录或缺少身份凭证")
    token = authorization.removeprefix("Bearer ").strip()

    # 向后兼容开发硬编码 token
    if token == "demo-token-admin":
        return {"user": "admin", "role": "admin"}

    try:
        import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(401, "登录已失效，请重新登录")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """明文与散列哈希密码对比 (支持向后兼容)"""
    if plain_password == hashed_password:
        return True
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# ---------- Pydantic v2 Models ----------

class LoginIn(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class ProfileUpdateIn(BaseModel):
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    location: str | None = None
    motto: str | None = None
    email: str | None = None
    avatar: str | None = None
    tags: list[str] | None = None
    socials: dict[str, Any] | None = None


class SkillIn(BaseModel):
    name: str
    level: int = 60
    category: str = "技术"


class ProjectIn(BaseModel):
    title: str
    description: str = ""
    cover: str = ""
    link: str = ""
    tags: list[str] = []
    featured: int = 0
    sort: int = 99


# ---------- 登录鉴权路由 ----------

@router.post("/auth/login")
def login(body: LoginIn):
    conn = get_db()
    u = row(conn, "SELECT * FROM users WHERE username=?", (body.username,))
    conn.close()

    if not u or not verify_password(body.password, u["password"]):
        raise HTTPException(401, "账号或密码错误")

    token_data = {"user": u["username"], "role": u["role"], "nickname": u["nickname"]}
    token = create_access_token(token_data)

    return {
        "token": token,
        "user": {"username": u["username"], "nickname": u["nickname"], "role": u["role"]}
    }


@router.get("/auth/me")
def me(authorization: str | None = Header(None)):
    user_info = require_admin(authorization)
    return {"user": user_info}


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
def update_profile(body: ProfileUpdateIn, authorization: str | None = Header(None)):
    require_admin(authorization)
    payload_dict = body.model_dump(exclude_unset=True)

    fields = ["name", "title", "bio", "location", "motto", "email", "avatar"]
    sets, params = [], []
    for f in fields:
        if f in payload_dict and payload_dict[f] is not None:
            sets.append(f"{f}=?")
            params.append(payload_dict[f])
    if "tags" in payload_dict and payload_dict["tags"] is not None:
        sets.append("tags=?")
        params.append(json.dumps(payload_dict["tags"], ensure_ascii=False))
    if "socials" in payload_dict and payload_dict["socials"] is not None:
        sets.append("socials=?")
        params.append(json.dumps(payload_dict["socials"], ensure_ascii=False))

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
def add_skill(body: SkillIn, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO skills(name,level,category) VALUES(?,?,?)",
        (body.name, body.level, body.category)
    )
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
def add_project(body: ProjectIn, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO projects(title,description,cover,link,tags,featured,sort) VALUES(?,?,?,?,?,?,?)",
        (body.title, body.description, body.cover, body.link,
         json.dumps(body.tags, ensure_ascii=False), body.featured, body.sort)
    )
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@router.put("/projects/{pid}")
def update_project(pid: int, body: ProjectIn, authorization: str | None = Header(None)):
    require_admin(authorization)
    conn = get_db()
    conn.execute(
        "UPDATE projects SET title=?,description=?,cover=?,link=?,tags=?,featured=?,sort=? WHERE id=?",
        (body.title, body.description, body.cover, body.link,
         json.dumps(body.tags, ensure_ascii=False), body.featured, body.sort, pid)
    )
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
