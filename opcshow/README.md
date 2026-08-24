# Opcshow - 现代风格 Web 个人动态主页与数字资产系统

[![Vue3](https://img.shields.io/badge/Vue.js-3.4-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white)](https://vuejs.org/) [![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/) [![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/) [![ECharts](https://img.shields.io/badge/ECharts-5.5-AA344D?style=flat-square&logo=apacheecharts&logoColor=white)](https://echarts.apache.org/) [![Three.js](https://img.shields.io/badge/Three.js-0.166-000000?style=flat-square&logo=threedotjs&logoColor=white)](https://threejs.org/)

---

## 📋 项目简介

**Opcshow** 是一套集**个人总览、知识管理、生活记录、娱乐收藏、社交互动与 AI 智能助手**于一体的现代高颜值 Web 动态主页与数字资产管理系统。项目基于前后端分离架构搭建，前端采用 Vue 3 + TypeScript + Vite + Glassmorphism 极简玻璃拟态设计，后端采用 Python FastAPI 结合 SQLite 轻量高可用持久层，内置基于规则引擎与大模型 API 预留接口的 AI 工具箱，支持管理后台一站式审核与数据监控。

---

## 🛠️ 技术栈

### 🖥️ 前端技术栈 (Web Frontend)

| 技术 / 库 | 版本 / 说明 | 用途与特性 |
| :--- | :--- | :--- |
| **Vue.js** | `^3.4.38` | 单页面应用核心框架（Composition API + Script Setup） |
| **TypeScript** | `^5.5.4` | 静态类型检查与代码强约束 |
| **Vite** | `^5.4.2` | 新一代极速前端构建工具 & 开发服务器 |
| **Vue Router** | `^4.4.3` | 单页面路由导航、路由守卫与权限拦截 |
| **ECharts** | `^5.5.1` | 运动数据、访问统计图表可视化渲染 |
| **Three.js** | `^0.166.1` | WebGL 3D 视觉场景与动态粒子/背景增强 |
| **SortableJS** | `^1.15.6` | 首页卡片拖拽重排与自定义布局保存 |
| **Vanilla CSS** | Modern CSS | 玻璃拟态 (Glassmorphism)、响应式 Flex/Grid 布局 |

### ⚙️ 后端技术栈 (Server Backend)

| 技术 / 库 | 版本 / 说明 | 用途与特性 |
| :--- | :--- | :--- |
| **Python** | `3.10+` | 服务端开发语言 |
| **FastAPI** | `^0.100.0` | 异步高性能 RESTful API 框架，自动生成 OpenAPI 文档 |
| **Uvicorn** | `^0.22.0` | ASGI 高性能 Web 服务器 |
| **SQLite 3** | 内置 | 轻量嵌入式关系数据库，原生支持 JSON 字段查询 |
| **Pydantic** | `^2.0` | 请求体与响应数据模型校验 |
| **Custom DAO** | `db.py` | 简洁高性能数据层封装，提供连接池管理与字典映射 |

### 🤖 AI 服务与智能引擎 (AI & Intelligence)

| 模块 / 功能 | 引擎实现 | 说明与应用场景 |
| :--- | :--- | :--- |
| **AI 创作助手** | 智能模板 + 本地规则 / 大模型 API | 快速生成文案、随笔、社交简介 |
| **文案润色** | 正感语义转换 / 大模型 API | 优化措辞、精简冗余表达、统一专业语气 |
| **简历 STAR 优化** | 结构化拆解引擎 / 大模型 API | 依据 STAR 法则提炼项目经验与量化成果 |
| **知识库问答** | 全文检索 + 关键词摘要匹配 | 关联内部知识库文章进行精准答疑 |
| **代码辅助** | 示例库 / 大模型 API | 常用前端/后端算法与工具函数代码提示 |
| **留言风控审核** | 敏感词规则引擎 / LLM 过滤 | 访客留言实时智能审核，自动分类上墙或待审核列 |

---

## 📁 目录结构

```text
opcshow/
├── server/                     # 后端 FastAPI 项目根目录
│   ├── main.py                 # FastAPI 入口文件、CORS 配置与全局异常处理
│   ├── db.py                   # 数据库初始化、建表 SQL、JSON 解析与 DAO 工具
│   ├── opcshow.db              # SQLite 数据库文件
│   └── routers/                # 业务路由模块划分
│       ├── __init__.py
│       ├── admin.py            # 后台数据统计、留言与友链审核
│       ├── ai.py               # AI 对话、文案润色、STAR 简历优化与代码生成
│       ├── core.py             # 登录鉴权、个人资料、技能、作品、布局与系统设置
│       ├── fun.py              # 音乐播放器、电影收藏、百宝箱外链
│       ├── knowledge.py        # 三级目录知识库与 Markdown 文章 CRUD/检索
│       ├── life.py             # 朋友圈动态、恋爱记录、旅拍地图、运动与游戏档案
│       └── social.py           # 友情链接、留言弹幕、成长时间轴、自媒体矩阵与分享
└── web/                        # 前端 Vue 3 项目根目录
    ├── index.html              # 页面 HTML 入口
    ├── package.json            # 依赖与脚本配置
    ├── tsconfig.json           # TypeScript 配置文件
    ├── vite.config.ts          # Vite 构建与服务代理配置
    └── src/
        ├── App.vue             # 根组件
        ├── main.ts             # 前端入口文件
        ├── store.ts            # 全局响应式状态与 Token 持久化管理
        ├── api/                # API 请求封装 (Fetch / HTTP client)
        ├── components/         # 独立通用组件（AI 助手弹窗、3D 视觉、弹幕层等）
        ├── layout/             # 响应式主布局与侧边/顶栏导航栏
        ├── router/             # Vue Router 路由拦截与权限控制
        ├── styles/             # 全局主题、玻璃拟态与 CSS 变量样式
        └── views/              # 页面视图层
            ├── HomeView.vue    # 首页（个人概览、动态卡片与布局拖拽）
            ├── AdminView.vue   # 后台管理综合控制台
            ├── LoginView.vue   # 管理员登录页面
            ├── work/           # 工作域：KnowledgeView (知识库), ResumeView (简历)
            ├── life/           # 生活域：MomentsView (朋友圈), LoveView (恋爱), TravelView (地图), SportsView (运动), GamesView (游戏)
            ├── fun/            # 娱乐域：MusicView (音乐盒), MoviesView (电影), BoxView (百宝箱)
            └── me/             # 我的域：LinksView (友链), MessagesView (留言弹幕), TimelineView (时间轴), MatrixView (自媒体矩阵)
```

---

## ⚡ 核心功能模块和工作流程

```mermaid
flowchart TD
    subgraph 前端展示与交互 (Vue 3 SPA)
        A[访客/管理员入口] --> B{路由选择}
        B -->|首页| C[个人总览 & 可拖拽卡片]
        B -->|工作| D[三级知识库 & 在线简历]
        B -->|生活| E[朋友圈/恋爱/旅拍地图/运动/游戏]
        B -->|娱乐| F[音乐盒/电影打分/百宝箱]
        B -->|我的| G[友链/留言弹幕/时间轴/自媒体]
        B -->|后台管理| H[数据统计 & 审核面板]
    end

    subgraph 后端 API 服务 (FastAPI Server)
        C & D & E & F & G & H -->|RESTful JSON| I[FastAPI 路由分发]
        I --> J[Core / Admin Router]
        I --> K[Knowledge / Life / Fun / Social Router]
        I --> L[AI Service Router]
    end

    subgraph 智能引擎与持久层 (Data & AI)
        J & K --> M[(SQLite 3 数据库)]
        L --> N{AI 模式分支}
        N -->|本地规则引擎| O[STAR 润色 / 敏感词风控]
        N -->|预留 LLM 协议| P[OpenAI 兼容 REST 大模型]
    end
```

### 1. 💼 工作与知识管理模块 (Work & KB)
- **三级分类知识库**：支持多层级目录组织，Markdown 格式解析，结合文章全文本关键字检索与阅读量实时统计。
- **在线简历生成器**：实时编辑个人履历、项目经历与技能图谱，支持预览导出与 STAR 法则 AI 一键润色优化。

### 2. 🌿 生活与兴趣记录模块 (Life & Moments)
- **朋友圈动态**：支持图文动态发布、情绪标签标记与在线点赞。
- **恋爱计时与里程碑**：计算相爱天数，倒序记录重要恋爱纪念事件。
- **旅拍地图与运动统计**：足迹标记与大盘数据展示；运动数据集成 ECharts 直观呈现卡路里与公里数趋势。
- **游戏档案**：汇总个人游戏平台、时长与成就勋章。

### 3. 🎵 娱乐与收藏百宝箱 (Fun & Box)
- **Web 音乐盒**：支持流媒体音乐在线播放、歌词联动与喜爱标记。
- **电影影评收藏**：按分类与观看状态过滤电影打分与简评。
- **百宝箱外链**：按分类归档实用优质开发工具与日常网址。

### 4. 💬 社交互动与智能风控 (Social & Messages)
- **留言弹幕墙**：访客提交留言弹幕，内置 AI 敏感词检测引擎。正常内容实时上墙，敏感表达自动划入待审核队列。
- **友情链接与自媒体矩阵**：提供友链在线申请与后台审核流程，展示多平台粉丝数与自媒体跳转矩阵。

### 5. 🤖 AI 智能对话助手 (AI Assistant)
- **6 大内置交互模式**：自由对话、内容创作、文案润色、知识答疑、简历 STAR 优化、代码辅助。
- **扩展性设计**：默认启动本地高效规则引擎，配置 `OPC_LLM_KEY` 环境变量后可无缝升级接入 DeepSeek / Qwen / GPT-4 等大模型。

---

## ⚙️ 部署指南

### 1. 环境准备

确保部署服务器已安装以下软件版本：
- **Python**: `3.10` 及以上
- **Node.js**: `18.0` 及以上 (推荐 `v20.x`)
- **Package Manager**: `npm` 或 `pnpm` / `yarn`

---

### 2. 后端部署 (FastAPI)

```bash
# 1. 进入后端目录
cd opcshow/server

# 2. 创建并激活 Python 虚拟环境 (Windows CMD / PowerShell)
python -m venv .venv
.venv\Scripts\activate

# 3. 安装后端依赖
pip install fastapi uvicorn pydantic

# 4. 启动后端 API 服务 (监听 8000 端口)
uvicorn main:app --host 0.0.0.0 --port 8000
```
> 后端服务成功启动后，浏览器访问 `http://127.0.0.1:8000/api/docs` 可查看交互式 Swagger API 文档。

---

### 3. 前端部署 (Vue 3 + Vite)

```bash
# 1. 进入前端目录
cd opcshow/web

# 2. 安装前端项目依赖
npm install

# 3. 开发模式启动 (热重载)
npm run dev

# 4. 生产环境打包
npm run build
```

打包完成后将在 `opcshow/web/dist` 目录下生成静态文件，可配合 **Nginx** 进行生产发布。

---

### 4. Nginx 生产环境配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 前端静态资源
    location / {
        root /var/www/opcshow/web/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 📦 API 接口概览

| 模块 | 方式 | 接口路径 | 鉴权要求 | 功能说明 |
| :--- | :---: | :--- | :---: | :--- |
| **核心** | `POST` | `/api/auth/login` | 否 | 管理员登录，获取 Token |
| **核心** | `GET` | `/api/profile` | 否 | 获取个人基本资料与社交信息 |
| **核心** | `PUT` | `/api/profile` | **是** | 更新个人资料与配置 |
| **核心** | `GET` | `/api/projects` | 否 | 获取项目/作品列表 |
| **核心** | `POST` | `/api/projects` | **是** | 新增项目作品 |
| **核心** | `GET` | `/api/layout` | 否 | 获取自定义卡片布局配置 |
| **核心** | `PUT` | `/api/layout` | **是** | 保存拖拽自定义布局配置 |
| **知识库** | `GET` | `/api/knowledge/categories` | 否 | 获取三级知识库分类树 |
| **知识库** | `GET` | `/api/knowledge/articles` | 否 | 获取知识库文章列表 (支持关键词搜索) |
| **知识库** | `POST` | `/api/knowledge/articles` | **是** | 发布 Markdown 知识库文章 |
| **生活** | `GET` | `/api/life/moments` | 否 | 获取朋友圈动态列表 |
| **生活** | `POST` | `/api/life/moments/{mid}/like` | 否 | 给朋友圈动态点赞 |
| **生活** | `GET` | `/api/life/sports` | 否 | 获取运动记录与分类统计 |
| **娱乐** | `GET` | `/api/fun/music` | 否 | 获取音乐播放列表 |
| **娱乐** | `GET` | `/api/fun/movies` | 否 | 获取电影收藏列表 |
| **社交** | `GET` | `/api/social/messages` | 否 | 获取已审核上墙的留言弹幕 |
| **社交** | `POST` | `/api/social/messages` | 否 | 提交留言（触发智能风控审核） |
| **AI服务** | `POST` | `/api/ai/chat` | 否 | AI 智能对话、文案润色与 STAR 简历优化 |
| **AI服务** | `GET` | `/api/ai/capabilities` | 否 | 获取 AI 引擎支持的能力与模式 |
| **后台** | `GET` | `/api/admin/stats` | **是** | 获取后台数据总量、访客趋势与待审队列 |
| **后台** | `POST` | `/api/admin/messages/{mid}/review`| **是** | 审核/驳回/置顶/回复留言 |

---

## 💡 总结与展望

### ✨ 亮点总结
1. **模块化与高度自由度**：涵盖知识、生活、娱乐、社交全维度数字资产，支持首页拖拽重新布局。
2. **前后端解耦与高性能**：前有 Vue 3 毫秒级响应与渲染，后有 FastAPI 极速 API 调度，轻量 SQLite 开箱即用。
3. **AI 原生集成与优雅回退**：内置风控、创作与 STAR 优化，无缝支持规则引擎与在线大模型切换。
4. **全端响应式与现代美学**：采用现代化 Glassmorphism 玻璃拟态设计，搭配 ECharts 与 Three.js 赋能视觉感知。

### 🚀 未来展望
- [ ] **RAG 向量检索**：引入 Chroma / FAISS 向量数据库，基于本地知识库实现精准问答与文档检索。
- [ ] **云存储扩展**：支持 S3 / OSS / GCS 协议，一键上传并托管高分辨率图床与视频资源。
- [ ] **多端适配与 PWA**：增强离线缓存支持，进一步适配移动端小程序与 App 视口体验。

---

> 💡 **项目链接**
> - **前台界面**: [http://localhost:5174/](http://localhost:5174/)
> - **后台管理登录**: [http://localhost:5174/login](http://localhost:5174/login) *(默认账号: `admin` / 密码: `admin123`)*
> - **后台控制台**: [http://localhost:5174/admin](http://localhost:5174/admin)
> - **API 文档 (Swagger)**: [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
