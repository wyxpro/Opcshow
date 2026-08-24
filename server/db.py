"""Opcshow 数据库层：SQLite 持久化 + Schema + 种子数据。
生产环境可平滑替换为 MySQL（PRD 指定），此处用 SQLite 实现零依赖运行。
所有表结构与 PRD 数据模型一一对应。
"""
import json
import os
import sqlite3
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/opcshow.db"
    seed_db = os.path.join(BASE_DIR, "opcshow.db")
    if not os.path.exists(DB_PATH) and os.path.exists(seed_db):
        import shutil
        shutil.copyfile(seed_db, DB_PATH)
else:
    DB_PATH = os.path.join(BASE_DIR, "opcshow.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  nickname TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user',
  avatar TEXT DEFAULT '',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT, title TEXT, bio TEXT, location TEXT, motto TEXT,
  avatar TEXT, email TEXT, tags TEXT, socials TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS skills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, level INTEGER DEFAULT 60, category TEXT DEFAULT '技术'
);
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL, description TEXT DEFAULT '', cover TEXT DEFAULT '',
  link TEXT DEFAULT '', tags TEXT DEFAULT '[]', featured INTEGER DEFAULT 0, sort INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS interests (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, icon TEXT, description TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS layouts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, config TEXT NOT NULL, active INTEGER DEFAULT 0, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS kb_categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, parent_id INTEGER DEFAULT 0, level INTEGER DEFAULT 1, sort INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS kb_articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER, title TEXT NOT NULL, summary TEXT DEFAULT '',
  content TEXT DEFAULT '', tags TEXT DEFAULT '[]', views INTEGER DEFAULT 0,
  created_at TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS resumes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, template TEXT DEFAULT 'minimal', data TEXT NOT NULL, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS moments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT NOT NULL, images TEXT DEFAULT '[]', location TEXT DEFAULT '',
  mood TEXT DEFAULT '', likes INTEGER DEFAULT 0, created_at TEXT
);
CREATE TABLE IF NOT EXISTS love_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL, event_date TEXT, description TEXT DEFAULT '',
  type TEXT DEFAULT 'memory', cover TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS love_meta (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  partner TEXT, start_date TEXT, story TEXT
);
CREATE TABLE IF NOT EXISTS travel_points (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, x REAL, y REAL, region TEXT DEFAULT '',
  visit_date TEXT, note TEXT DEFAULT '', photos TEXT DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS sports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL, sport_date TEXT, value REAL DEFAULT 0,
  unit TEXT DEFAULT 'km', duration INTEGER DEFAULT 0, note TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS games (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, platform TEXT DEFAULT '', role TEXT DEFAULT '',
  level TEXT DEFAULT '', hours INTEGER DEFAULT 0, achievement TEXT DEFAULT '', cover TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS music (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL, artist TEXT DEFAULT '', album TEXT DEFAULT '',
  url TEXT NOT NULL, cover TEXT DEFAULT '', duration INTEGER DEFAULT 0, liked INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS movies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL, category TEXT DEFAULT '剧情', rating REAL DEFAULT 8.0,
  year INTEGER DEFAULT 2024, poster TEXT DEFAULT '', comment TEXT DEFAULT '',
  status TEXT DEFAULT '已看', director TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS box_categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, icon TEXT DEFAULT '✦', sort INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS box_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER, title TEXT NOT NULL, url TEXT DEFAULT '', description TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS friend_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, url TEXT NOT NULL, avatar TEXT DEFAULT '',
  description TEXT DEFAULT '', status TEXT DEFAULT 'approved', created_at TEXT
);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nickname TEXT NOT NULL, content TEXT NOT NULL, color TEXT DEFAULT '#E4572E',
  likes INTEGER DEFAULT 0, pinned INTEGER DEFAULT 0, reply TEXT DEFAULT '',
  status TEXT DEFAULT 'approved', created_at TEXT
);
CREATE TABLE IF NOT EXISTS timeline (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_date TEXT NOT NULL, title TEXT NOT NULL, description TEXT DEFAULT '', tag TEXT DEFAULT '成长'
);
CREATE TABLE IF NOT EXISTS social_accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL, handle TEXT DEFAULT '', url TEXT DEFAULT '',
  followers TEXT DEFAULT '0', icon TEXT DEFAULT '', description TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS visits (
  id INTEGER PRIMARY KEY AUTOINCREMENT, visit_date TEXT UNIQUE, count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY, value TEXT
);
"""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows(conn, sql, params=()):
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def row(conn, sql, params=()):
    r = conn.execute(sql, params).fetchone()
    return dict(r) if r else None


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def seed(conn):
    """首次启动写入演示数据，让产品开箱即用。"""
    today = datetime.now()
    d = lambda days: (today - timedelta(days=days)).strftime("%Y-%m-%d")

    conn.execute(
        "INSERT INTO users(username,password,nickname,role) VALUES('admin','admin123','站长','admin')"
    )
    conn.execute(
        """INSERT INTO profile(id,name,title,bio,location,motto,avatar,email,tags,socials,updated_at)
        VALUES(1,?,?,?,?,?,?,?,?,?,?)""",
        (
            "林一舟", "全栈工程师 / 内容创作者",
            "热爱构建有温度的数字产品。白天写代码，晚上写字、拍照、跑步，偶尔在虚拟世界里冒险。这个主页是我的数字自留地，记录成长、作品与生活的全部痕迹。",
            "杭州 · 中国", "保持热爱，奔赴山海。",
            "", "hi@yizhou.dev",
            json.dumps(["前端开发", "摄影", "马拉松", "独立开发", "咖啡"], ensure_ascii=False),
            json.dumps({"github": "github.com/linyizhou", "weibo": "@林一舟"}, ensure_ascii=False),
            now(),
        ),
    )
    skills = [("Vue / TypeScript", 92, "前端"), ("Node.js / Python", 86, "后端"),
              ("UI 设计", 74, "设计"), ("Three.js 可视化", 68, "可视化"),
              ("写作表达", 80, "创作"), ("项目管理", 72, "协作")]
    conn.executemany("INSERT INTO skills(name,level,category) VALUES(?,?,?)", skills)
    projects = [
        ("Opcshow 个人主页系统", "零代码拖拽式个人动态主页，聚合展示、记录与社交的一体化平台",
         "https://picsum.photos/seed/opcshow/640/400", "https://demo.opcshow.cn",
         '["Vue3","FastAPI","Three.js"]', 1, 1),
        ("Pulse 跑步数据看板", "面向跑者的训练数据可视化工具，支持心率区间与配速分析",
         "https://picsum.photos/seed/pulse/640/400", "", '["ECharts","数据可视化"]', 1, 2),
        ("拾光相册", "旅拍照片与地图点位绑定的轻量相册应用",
         "https://picsum.photos/seed/album/640/400", "", '["地图","WebGL"]', 0, 3),
        ("Inkflow 写作助手", "极简 Markdown 写作工具，专注沉浸写作体验",
         "https://picsum.photos/seed/ink/640/400", "", '["编辑器","效率"]', 0, 4),
    ]
    conn.executemany(
        "INSERT INTO projects(title,description,cover,link,tags,featured,sort) VALUES(?,?,?,?,?,?,?)",
        projects)
    interests = [("摄影", "◐", "街头与人文，用取景框收藏城市的光"),
                 ("跑步", "◈", "月跑量 120km，目标全马破四"),
                 ("咖啡", "◑", "手冲爱好者，耶加雪菲是本命"),
                 ("游戏", "◉", "主机党，偏爱开放世界与独立游戏"),
                 ("阅读", "◍", "偏爱科幻与传记，年均 30 本"),
                 ("徒步", "◎", "走过武功山与雨崩，下一站冈仁波齐")]
    conn.executemany("INSERT INTO interests(name,icon,description) VALUES(?,?,?)", interests)

    default_layout = [
        {"id": "profile", "title": "个人资料", "span": 4},
        {"id": "skills", "title": "技能雷达", "span": 4},
        {"id": "works", "title": "作品集", "span": 4},
        {"id": "interests", "title": "兴趣爱好", "span": 6},
        {"id": "stats", "title": "数据概览", "span": 6},
    ]
    conn.execute(
        "INSERT INTO layouts(name,config,active,updated_at) VALUES('默认布局',?,1,?)",
        (json.dumps(default_layout, ensure_ascii=False), now()))

    # 知识库三级目录
    cats = [
        (1, "前端开发", 0, 1, 1), (2, "后端工程", 0, 1, 2), (3, "生活随笔", 0, 1, 3),
        (4, "Vue 生态", 1, 2, 1), (5, "工程化", 1, 2, 2),
        (6, "Python", 2, 2, 1), (7, "数据库", 2, 2, 2),
        (8, "城市漫游", 3, 2, 1), (9, "读书笔记", 3, 2, 2),
        (10, "Composition API", 4, 3, 1), (11, "状态管理", 4, 3, 2),
        (12, "FastAPI 实践", 6, 3, 1),
    ]
    conn.executemany(
        "INSERT INTO kb_categories(id,name,parent_id,level,sort) VALUES(?,?,?,?,?)", cats)
    articles = [
        (10, "组合式函数的设计哲学", "如何写出可复用、可测试的 composable",
         "# 组合式函数的设计哲学\n\n组合式函数（composable）是 Vue3 复用逻辑的核心载体。\n\n## 三个原则\n\n1. **单一职责**：一个 composable 只做一件事，如 `useMouse` 只追踪坐标。\n2. **显式依赖**：参数即依赖，返回值即能力，避免隐式全局状态。\n3. **响应式透明**：接收 ref 或普通值都要工作正常，内部用 `toValue` 归一化。\n\n## 命名约定\n\n以 `use` 开头，返回对象便于解构重命名。\n\n```ts\nexport function useCounter(initial = 0) {\n  const count = ref(initial)\n  const inc = () => count.value++\n  return { count, inc }\n}\n```\n\n好的 composable 像积木：小、稳、可组合。",
         '["Vue3","Composable"]', 328, d(30)),
        (10, "script setup 语法糖全解", "从编译视角理解 Vue3 单文件组件",
         "# script setup 语法糖全解\n\n`<script setup>` 是编译时语法糖，代码在 `setup()` 上下文中执行。\n\n## 核心要点\n\n- 顶层绑定自动暴露给模板\n- `defineProps` / `defineEmits` 是编译宏，无需导入\n- 默认关闭实例暴露，用 `defineExpose` 显式开放\n\n## 与 TS 的配合\n\n```ts\nconst props = defineProps<{ title: string; count?: number }>()\nconst emit = defineEmits<{ change: [value: number] }>()\n```\n\n编译产物更精简，类型推导更完整，这是推荐写法的根本原因。",
         '["Vue3","SFC"]', 256, d(22)),
        (11, "Pinia 的状态设计范式", "从 Options 到 Setup Store 的迁移实践",
         "# Pinia 的状态设计范式\n\n## Store 划分原则\n\n按**业务域**而非数据类型划分：user、cart、order 各自独立。\n\n## Setup Store 写法\n\n```ts\nexport const useUserStore = defineStore('user', () => {\n  const profile = ref(null)\n  const isLogin = computed(() => !!profile.value)\n  async function fetchProfile() { /* ... */ }\n  return { profile, isLogin, fetchProfile }\n})\n```\n\n## 持久化\n\n路由级别按需持久化，避免全量 localStorage 带来的同步开销。",
         '["Pinia","状态管理"]', 189, d(15)),
        (12, "FastAPI 依赖注入实战", "用 Depends 构建可测试的接口层",
         "# FastAPI 依赖注入实战\n\n依赖注入是 FastAPI 最优雅的设计。\n\n## 数据库会话注入\n\n```python\ndef get_db():\n    db = SessionLocal()\n    try:\n        yield db\n    finally:\n        db.close()\n\n@app.get('/users')\ndef list_users(db = Depends(get_db)):\n    ...\n```\n\n## 鉴权依赖\n\n把 token 校验写成依赖项，业务接口零侵入获得鉴权能力。测试时用 `dependency_overrides` 替换为内存实现。",
         '["FastAPI","Python"]', 412, d(10)),
        (7, "索引失效的七种场景", "MySQL 慢查询排查笔记",
         "# 索引失效的七种场景\n\n1. 对索引列使用函数：`WHERE DATE(create_time) = '2024-01-01'`\n2. 隐式类型转换：字符串列用数字查询\n3. 前导模糊匹配：`LIKE '%abc'`\n4. 联合索引不满足最左前缀\n5. OR 连接非索引列\n6. 负向条件 `!=` `NOT IN` 大范围扫描\n7. 优化器评估全表更快时主动放弃索引\n\n## 排查工具\n\n`EXPLAIN` 看 type 与 key，`slow log` 定位慢语句。",
         '["MySQL","索引"]', 567, d(8)),
        (8, "城市漫游：杭州篇", "西湖以西，烟火以东",
         "# 城市漫游：杭州篇\n\n杭州的可爱在于湖与城的边界是模糊的。\n\n## 路线\n\n北山街出发 → 断桥 → 孤山 → 杨公堤，最后拐进茅家埠。\n\n清晨六点的北山街属于跑步的人，梧桐叶把阳光筛成碎金。茅家埠的茶馆里，老板用虎跑水泡龙井，一坐就是一整个下午。\n\n> 城市漫游的意义，是把「经过」变成「在场」。",
         '["随笔","旅行"]', 145, d(5)),
        (9, "《人类简史》读书笔记", "认知革命如何重塑智人",
         "# 《人类简史》读书笔记\n\n赫拉利的核心洞见：**虚构的能力**让智人实现了大规模协作。\n\n## 三个革命\n\n- 认知革命：语言与虚构故事\n- 农业革命：史上最大的「骗局」？\n- 科学革命：承认无知的力量\n\n金钱、国家、公司，本质上都是集体想象。这不是贬低，而是理解文明运作的钥匙。",
         '["读书","历史"]', 203, d(3)),
    ]
    conn.executemany(
        """INSERT INTO kb_articles(category_id,title,summary,content,tags,views,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?)""",
        [(*a, now()) for a in articles])

    resume_data = {
        "basic": {"name": "林一舟", "title": "全栈工程师", "phone": "138-0000-0000",
                  "email": "hi@yizhou.dev", "location": "杭州", "years": "5 年经验"},
        "summary": "5 年全栈开发经验，主导过 3 个从 0 到 1 的 Web 产品，擅长 Vue 生态与 Python 服务端，关注性能优化与工程化提效。",
        "education": [{"school": "浙江大学", "major": "计算机科学与技术", "period": "2015-2019", "degree": "本科"}],
        "experience": [
            {"company": "某一线互联网公司", "role": "高级前端工程师", "period": "2021.03 - 至今",
             "desc": "负责核心商业化产品线前端架构，推动组件库与微前端落地，页面性能提升 40%，带领 4 人小组完成 20+ 迭代。"},
            {"company": "创业公司（A轮）", "role": "全栈工程师", "period": "2019.07 - 2021.02",
             "desc": "独立负责 SaaS 产品前后端开发，搭建 CI/CD 与监控体系，支撑 0 到 10 万用户的增长。"},
        ],
        "projects": [
            {"name": "Opcshow 个人主页系统", "role": "独立开发", "period": "2025",
             "desc": "零代码拖拽个人主页平台，Vue3 + FastAPI 架构，集成 3D 特效与 AI 助手。"}
        ],
        "skills": ["Vue3 / TypeScript", "Node.js / Python", "MySQL / Redis", "Three.js / ECharts", "Docker / CI-CD"],
    }
    conn.execute(
        "INSERT INTO resumes(name,template,data,updated_at) VALUES('我的简历','minimal',?,?)",
        (json.dumps(resume_data, ensure_ascii=False), now()))

    moments = [
        ("凌晨两点终于把拖拽布局的最后一个 bug 修完了，窗外下起了小雨。记录一下这个瞬间。",
         '["https://picsum.photos/seed/night/500/300"]', "杭州", "满足", 24, d(1)),
        ("周末龙井村徒步 12km，满山的茶园绿得不像话，随手拍都是壁纸。",
         '["https://picsum.photos/seed/tea1/500/300","https://picsum.photos/seed/tea2/500/300","https://picsum.photos/seed/tea3/500/300"]',
         "龙井村", "开心", 56, d(3)),
        ("读完了《克拉拉与太阳》，石黑一雄太会写「克制的深情」了。",
         "[]", "", "感触", 31, d(6)),
        ("新玩具到手：手冲壶 + 耶加雪菲，水温 92°，三段注水，今天这杯有柑橘的尾韵。",
         '["https://picsum.photos/seed/coffee/500/300"]', "家里", "惬意", 42, d(9)),
        ("半马 PB！1:52:36，最后 3 公里靠意志力顶下来的。下一个目标：全马。",
         '["https://picsum.photos/seed/run/500/300"]', "钱塘江畔", "兴奋", 88, d(14)),
    ]
    conn.executemany(
        "INSERT INTO moments(content,images,location,mood,likes,created_at) VALUES(?,?,?,?,?,?)",
        moments)

    conn.execute(
        "INSERT INTO love_meta(id,partner,start_date,story) VALUES(1,?,?,?)",
        ("苏晚", "2021-10-16", "在朋友的摄影展上认识，她拍的《雨夜公交站》让我驻足了很久。后来那幅照片挂在了我们家的客厅。"))
    love_events = [
        ("初次相遇", "2021-10-16", "南山路摄影展，她在自己的作品前给我讲构图", "memory",
         "https://picsum.photos/seed/love1/500/300"),
        ("第一次旅行", "2022-04-05", "清明假期去了大理，环洱海骑行 60 公里", "travel",
         "https://picsum.photos/seed/love2/500/300"),
        ("在一起 1000 天", "2024-07-12", "她偷偷做了纪念册，从第一张合照开始", "anniversary",
         "https://picsum.photos/seed/love3/500/300"),
        ("领养「拿铁」", "2024-11-20", "家里多了只橘猫，取名拿铁，现在是真正的主子", "memory",
         "https://picsum.photos/seed/love4/500/300"),
    ]
    conn.executemany(
        "INSERT INTO love_events(title,event_date,description,type,cover) VALUES(?,?,?,?,?)",
        love_events)

    travel = [
        ("大理 · 洱海", 73, 68, "云南", "2022-04-05", "环海西路的风把云吹得很快",
         '["https://picsum.photos/seed/dali1/400/300","https://picsum.photos/seed/dali2/400/300"]'),
        ("重庆 · 洪崖洞", 62, 55, "重庆", "2023-05-01", "夜景像《千与千寻》的汤屋",
         '["https://picsum.photos/seed/cq1/400/300"]'),
        ("青岛 · 八大关", 70, 24, "山东", "2023-10-02", "秋天的梧桐和海风是绝配",
         '["https://picsum.photos/seed/qd1/400/300","https://picsum.photos/seed/qd2/400/300","https://picsum.photos/seed/qd3/400/300"]'),
        ("京都 · 哲学之道", 86, 32, "日本", "2024-03-28", "樱花落成河，一路走一路安静",
         '["https://picsum.photos/seed/kyoto1/400/300","https://picsum.photos/seed/kyoto2/400/300"]'),
        ("武功山", 55, 60, "江西", "2024-09-15", "高山草甸上看了一场完整日出",
         '["https://picsum.photos/seed/wg1/400/300"]'),
        ("喀什古城", 18, 42, "新疆", "2025-06-20", "土黄色的巷子里全是生活的声音",
         '["https://picsum.photos/seed/kashi1/400/300","https://picsum.photos/seed/kashi2/400/300"]'),
    ]
    conn.executemany(
        "INSERT INTO travel_points(name,x,y,region,visit_date,note,photos) VALUES(?,?,?,?,?,?,?)",
        travel)

    sports = []
    for i, (t, v) in enumerate([("跑步", 8.2), ("跑步", 10.5), ("骑行", 32.0), ("跑步", 6.4),
                                ("游泳", 1.5), ("跑步", 12.0), ("骑行", 45.0), ("跑步", 8.8),
                                ("徒步", 15.2), ("跑步", 21.1)]):
        sports.append((t, d(2 + i * 3), v, "km", int(v * 6) + 20, ""))
    conn.executemany(
        "INSERT INTO sports(type,sport_date,value,unit,duration,note) VALUES(?,?,?,?,?,?)", sports)

    games = [
        ("塞尔达传说：王国之泪", "Switch", "林克", "通关 · 全神庙", 185, "大师之剑全强化",
         "https://picsum.photos/seed/zelda/400/240"),
        ("艾尔登法环", "PS5", "流浪骑士", "Lv.150", 230, "三周目 · 全追忆",
         "https://picsum.photos/seed/elden/400/240"),
        ("星露谷物语", "PC", "农场主", "第 5 年", 120, "完美度 100%",
         "https://picsum.photos/seed/stardew/400/240"),
        ("双人成行", "PS5", "科迪", "通关", 18, "和她一起打完了所有小游戏",
         "https://picsum.photos/seed/ittakes2/400/240"),
    ]
    conn.executemany(
        "INSERT INTO games(name,platform,role,level,hours,achievement,cover) VALUES(?,?,?,?,?,?,?)",
        games)

    music = [
        ("SoundHelix Song 1", "SoundHelix", "Demo", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
         "https://picsum.photos/seed/m1/300/300", 372, 1),
        ("SoundHelix Song 2", "SoundHelix", "Demo", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
         "https://picsum.photos/seed/m2/300/300", 305, 0),
        ("SoundHelix Song 3", "SoundHelix", "Demo", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
         "https://picsum.photos/seed/m3/300/300", 344, 1),
    ]
    conn.executemany(
        "INSERT INTO music(title,artist,album,url,cover,duration,liked) VALUES(?,?,?,?,?,?,?)", music)

    movies = [
        ("星际穿越", "科幻", 9.4, 2014, "https://picsum.photos/seed/interstellar/300/420",
         "爱是唯一可以穿越时间与空间的东西。三刷依旧泪目。", "已看", "诺兰"),
        ("千与千寻", "动画", 9.4, 2001, "https://picsum.photos/seed/spirited/300/420",
         "每年夏天重看一次，每次都有新的感受。", "已看", "宫崎骏"),
        ("白日梦想家", "剧情", 8.6, 2013, "https://picsum.photos/seed/walter/300/420",
         "看完直接订了去冰岛的机票（虽然最后没去成）。", "已看", "本·斯蒂勒"),
        ("沙丘 2", "科幻", 8.2, 2024, "https://picsum.photos/seed/dune/300/420",
         "视听语言的巅峰，IMAX 厅值回票价。", "已看", "维伦纽瓦"),
        ("机器人总动员", "动画", 9.3, 2008, "https://picsum.photos/seed/walle/300/420",
         "前 40 分钟几乎没有对白，却是皮克斯最浪漫的段落。", "想看", "安德鲁·斯坦顿"),
    ]
    conn.executemany(
        "INSERT INTO movies(title,category,rating,year,poster,comment,status,director) VALUES(?,?,?,?,?,?,?,?)",
        movies)

    box_cats = [(1, "开发工具", "⌘", 1), (2, "设计灵感", "✦", 2), (3, "效率方法", "◈", 3), (4, "有趣网站", "☼", 4)]
    conn.executemany("INSERT INTO box_categories(id,name,icon,sort) VALUES(?,?,?,?)", box_cats)
    box_items = [
        (1, "Excalidraw", "https://excalidraw.com", "手绘风格白板，画架构图神器"),
        (1, "Regex101", "https://regex101.com", "正则表达式在线调试"),
        (2, "Awwwards", "https://awwwards.com", "全球顶尖网页设计灵感"),
        (2, "Mobbin", "https://mobbin.com", "移动端 UI 模式库"),
        (3, "滴答清单", "https://dida365.com", "GTD 实践主力工具"),
        (3, "Zettelkasten 方法", "", "卡片盒笔记法，知识复利"),
        (4, "Window Swap", "https://window-swap.com", "透过世界各地陌生人的窗户看风景"),
        (4, "Radio Garden", "https://radio.garden", "转动地球听全球电台"),
    ]
    conn.executemany(
        "INSERT INTO box_items(category_id,title,url,description) VALUES(?,?,?,?)", box_items)

    links = [
        ("陈默的技术博客", "https://blog.example.com/chenmo", "", "专注 Rust 与系统编程的老朋友", "approved", d(60)),
        ("晚风摄影集", "https://photo.example.com/wan", "", "她的主页，人像与街拍", "approved", d(45)),
        ("阿凯的独立开发日记", "https://indie.example.com/kai", "", "一个人做产品的第 900 天", "approved", d(30)),
        ("背包客小站", "https://travel.example.com", "", "徒步路线与装备清单", "pending", d(2)),
    ]
    conn.executemany(
        "INSERT INTO friend_links(name,url,avatar,description,status,created_at) VALUES(?,?,?,?,?,?)",
        links)

    msgs = [
        ("路过的风", "主页也太好看了吧！拖拽编辑求教程", "#E4572E", 12, 1, "谢谢！知识库里有相关文章", "approved", d(6)),
        ("前端小学生", "雷达图是用 ECharts 做的吗？配色好舒服", "#3D7A5E", 8, 0, "是的，主题色自定义的", "approved", d(5)),
        ("一只橘猫", "拿铁好可爱！我家也是橘猫哈哈哈", "#E8A13C", 15, 0, "", "approved", d(4)),
        ("大理客栈老板", "看到洱海的照片了，欢迎再来！", "#2E86AB", 6, 0, "一定！", "approved", d(3)),
        ("跑友-Leo", "半马 152 厉害，全马加油！", "#8A5CF6", 9, 0, "", "approved", d(2)),
        ("夜航西飞", "从友链摸过来的，内容好丰富，关注了", "#D4577A", 4, 0, "", "approved", d(1)),
        ("匿名访客", "这个留言弹幕的形式好有创意", "#5B8C5A", 3, 0, "", "approved", d(0)),
        ("广告君", "代开发票加微信 xxx", "#999999", 0, 0, "", "pending", d(0)),
    ]
    conn.executemany(
        "INSERT INTO messages(nickname,content,color,likes,pinned,reply,status,created_at) VALUES(?,?,?,?,?,?,?,?)",
        msgs)

    timeline = [
        ("2015-09-01", "入学浙大", "计算机系报到，第一次住校", "学业"),
        ("2018-06-20", "第一次独立上线产品", "课程设计拿了年级第一，决定做工程师", "职业"),
        ("2019-07-15", "第一份工作", "加入创业公司，工位在窗边", "职业"),
        ("2021-03-01", "跳槽大厂", "开始带项目，也开始了真正的成长", "职业"),
        ("2021-10-16", "遇见她", "南山路的摄影展", "生活"),
        ("2023-04-16", "首个半马", "2:10:33，跑完在终点坐了很久", "运动"),
        ("2025-08-01", "启动 Opcshow", "想给每个人一个数字自留地", "作品"),
    ]
    conn.executemany(
        "INSERT INTO timeline(event_date,title,description,tag) VALUES(?,?,?,?)", timeline)

    accounts = [
        ("微信公众号", "一舟写字的地方", "https://mp.example.com", "1.2w", "✍", "周更长文，技术与生活"),
        ("Bilibili", "林一舟", "https://bilibili.example.com", "3.4w", "▶", "编程教程与装备测评"),
        ("GitHub", "linyizhou", "https://github.com/linyizhou", "2.1k", "⌥", "开源项目与代码片段"),
        ("小红书", "一舟跑不快", "https://red.example.com", "8.6k", "◉", "跑步与咖啡日常"),
        ("知乎", "林一舟", "https://zhihu.example.com", "5.2k", "◈", "前端话题优秀答主"),
    ]
    conn.executemany(
        "INSERT INTO social_accounts(platform,handle,url,followers,icon,description) VALUES(?,?,?,?,?,?)",
        accounts)

    for i in range(29, -1, -1):
        base = 120 + (i * 7) % 80
        conn.execute("INSERT OR IGNORE INTO visits(visit_date,count) VALUES(?,?)", (d(i), base))

    settings = {
        "site": {"name": "Opcshow", "subtitle": "林一舟的数字自留地", "icp": ""},
        "effects": {"three": True, "intensity": 0.6, "style": "particles"},
        "theme": {"accent": "#E4572E"},
        "carousel": {"interval": 4},
        "ai": {"enabled": True, "welcome": "你好，我是小舟助手，可以帮你创作文案、润色内容、优化简历。"},
    }
    for k, v in settings.items():
        conn.execute("INSERT INTO settings(key,value) VALUES(?,?)", (k, json.dumps(v, ensure_ascii=False)))


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    if conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"] == 0:
        seed(conn)
        conn.commit()
    conn.close()
