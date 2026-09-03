<script setup lang="ts">
/**
 * 专业的现代级后台管理系统 (Admin Console)
 * 采用左侧固定纵向菜单 + 顶部 Header + 快捷界面与内容配置面板
 */
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, fmtDate, setToken, type KbArticle, type Profile, type Project } from '../api'
import { useChart } from '../components/useChart'
import { applyAccent, store, toast } from '../store'

const router = useRouter()

// 侧边栏当前选中的 Active Menu
const activeMenu = ref('dashboard')
const collapsed = ref(false)

// 数据声明
const stats = ref<any>(null)
const messages = ref<any[]>([])
const links = ref<any[]>([])
const articles = ref<KbArticle[]>([])
const projects = ref<Project[]>([])
const profile = ref<Profile | null>(null)
const layoutConfig = ref<any[]>([])
const msgFilter = ref('pending') // pending | approved | rejected | all

// 图表 DOM
const visitChartEl = ref<HTMLElement | null>(null)

// 编辑 Modal 状态
const showArticleModal = ref(false)
const articleForm = ref<any>({ id: null, title: '', category_id: 10, summary: '', content: '', tags: [] })

const showProjectModal = ref(false)
const projectForm = ref<any>({ id: null, title: '', description: '', cover: '', link: '', tags: [], featured: 0 })

// 侧边栏菜单定义
const menuItems = [
  { id: 'dashboard', label: '控制台总览', icon: 'M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8v-10h-8v10zm0-18v6h8V3h-8z' },
  { id: 'layout', label: '界面与快捷配置', icon: 'M4 5h16v3H4zM4 11h10v8H4zM16 11h4v8h-4z' },
  { id: 'messages', label: '留言风控审核', icon: 'M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z', badgeKey: 'messages' },
  { id: 'links', label: '友情链接管理', icon: 'M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z', badgeKey: 'links' },
  { id: 'articles', label: '知识库文章', icon: 'M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z' },
  { id: 'projects', label: '作品项目集', icon: 'M4 6h16v12H4zM2 4v16h20V4H2zm9 5h2v6h-2z' },
  { id: 'profile', label: '站长与系统设置', icon: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' },
]

// 访问统计 ECharts 渲染
useChart(visitChartEl, () => ({
  grid: { left: 44, right: 20, top: 30, bottom: 30 },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: (stats.value?.visits || []).map((v: any) => v.visit_date.slice(5)),
    axisLabel: { color: '#8C9099', fontSize: 11 },
    axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
    axisLabel: { color: '#8C9099', fontSize: 11 },
  },
  series: [{
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    data: (stats.value?.visits || []).map((v: any) => v.count),
    lineStyle: { color: '#E4572E', width: 3 },
    itemStyle: { color: '#E4572E' },
    areaStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(228,87,46,0.35)' },
          { offset: 1, color: 'rgba(228,87,46,0)' }
        ]
      }
    },
  }],
}))

// 数据加载与初始化
async function reloadData() {
  try {
    stats.value = await api.get('/admin/stats')
    messages.value = await api.get('/social/messages?all=true')
    links.value = await api.get('/social/links?all=true')
    const artRes = await api.get('/knowledge/articles?page=1&size=50')
    articles.value = artRes.list || []
    projects.value = await api.get('/projects')
    profile.value = await api.get('/profile')
    const layoutRes = await api.get('/layout')
    layoutConfig.value = layoutRes?.config || []
  } catch (err: any) {
    toast(`加载数据失败: ${err.message}`, 'warn')
  }
}

// 留言审核动作
async function reviewMsg(m: any, action: string) {
  if (action === 'reply') {
    const reply = prompt('回复内容', m.reply || '')
    if (reply === null) return
    await api.post(`/admin/messages/${m.id}/review`, { action, reply })
  } else {
    await api.post(`/admin/messages/${m.id}/review`, { action })
  }
  toast('操作成功', 'ok')
  reloadData()
}

// 友链审核动作
async function reviewLink(l: any, status: string) {
  await api.put(`/social/links/${l.id}`, { status })
  toast('状态已更新', 'ok')
  reloadData()
}

async function delLink(l: any) {
  if (!confirm(`确定删除友链「${l.name}」吗？`)) return
  await api.del(`/social/links/${l.id}`)
  toast('已删除', 'ok')
  reloadData()
}

// 快捷配置保存
const accents = ['#E4572E', '#3D7A5E', '#D9932C', '#2E86AB', '#D4577A', '#23262B']
async function saveEffectsAndTheme() {
  await api.put('/settings/effects', { value: store.settings.effects })
  await api.put('/settings/theme', { value: store.settings.theme })
  await api.put('/settings/ai', { value: store.settings.ai })
  applyAccent()
  toast('配置已实时生效', 'ok')
}

// 卡片布局保存
async function saveLayoutSpan(id: string, span: number) {
  const item = layoutConfig.value.find((x) => x.id === id)
  if (item) item.span = span
  await api.put('/layout', { config: layoutConfig.value })
  toast('布局已保存', 'ok')
}

// 站长 Profile 保存
async function saveProfile() {
  if (!profile.value) return
  await api.put('/profile', profile.value)
  toast('个人资料已修改', 'ok')
}

// 精选项目切换
async function toggleFeatured(p: Project) {
  const newFeatured = p.featured === 1 ? 0 : 1
  await api.put(`/projects/${p.id}`, { ...p, featured: newFeatured })
  p.featured = newFeatured
  toast('项目状态已改变', 'ok')
}

// 删除文章
async function delArticle(a: KbArticle) {
  if (!confirm(`确定删除文章《${a.title}》吗？`)) return
  await api.del(`/knowledge/articles/${a.id}`)
  toast('文章已删除', 'ok')
  reloadData()
}

// 过滤后的留言
const filteredMessages = computed(() => {
  if (msgFilter.value === 'all') return messages.value
  return messages.value.filter((m) => m.status === msgFilter.value)
})

function logout() {
  setToken('')
  router.push('/login')
}

onMounted(reloadData)
</script>

<template>
  <div class="admin-console-wrap">
    <!-- ===== 左侧固定纵向菜单栏 (Left Sidebar) ===== -->
    <aside class="admin-sidebar" :class="{ collapsed: collapsed }">
      <div class="sidebar-head">
        <div class="sidebar-logo">
          <i></i>
          <span v-if="!collapsed">Opcshow<b>Console</b></span>
        </div>
        <button class="toggle-btn" @click="collapsed = !collapsed">
          <svg viewBox="0 0 24 24"><path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/></svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="item in menuItems"
          :key="item.id"
          class="nav-btn"
          :class="{ active: activeMenu === item.id }"
          @click="activeMenu = item.id"
        >
          <svg viewBox="0 0 24 24"><path :d="item.icon" /></svg>
          <span v-if="!collapsed">{{ item.label }}</span>
          <!-- 待处理徽章 -->
          <i v-if="!collapsed && item.badgeKey === 'messages' && stats?.pending?.messages" class="badge">
            {{ stats.pending.messages }}
          </i>
          <i v-if="!collapsed && item.badgeKey === 'links' && stats?.pending?.links" class="badge">
            {{ stats.pending.links }}
          </i>
        </button>
      </nav>

      <div class="sidebar-foot" v-if="!collapsed">
        <div class="admin-profile">
          <span class="avatar">舟</span>
          <div class="info">
            <strong>林一舟</strong>
            <small>超级管理员</small>
          </div>
        </div>
        <button class="logout-icon-btn" title="退出登录" @click="logout">
          <svg viewBox="0 0 24 24" width="18" height="18"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z" fill="currentColor"/></svg>
        </button>
      </div>
    </aside>

    <!-- ===== 右侧主工作区 (Main Content Area) ===== -->
    <main class="admin-main">
      <!-- 顶部 Top Header Bar -->
      <header class="admin-header">
        <div class="breadcrumb">
          <span class="muted">控制台</span> / <strong>{{ menuItems.find(m => m.id === activeMenu)?.label }}</strong>
        </div>

        <div class="header-actions">
          <button class="btn btn-secondary btn-sm" @click="reloadData">
            <svg viewBox="0 0 24 24" width="14" height="14" style="margin-right:4px"><path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/></svg>
            刷新数据
          </button>
          <a class="btn btn-primary btn-sm" href="/" target="_blank">
            <svg viewBox="0 0 24 24" width="14" height="14" style="margin-right:4px"><path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z" fill="currentColor"/></svg>
            访问前台主页
          </a>
        </div>
      </header>

      <div class="admin-body">
        <!-- ===== 1. 控制台总览 (Dashboard) ===== -->
        <section v-if="activeMenu === 'dashboard'" class="section-pane">
          <div v-if="stats" class="stat-grid">
            <div class="kpi-card">
              <div class="kpi-icon visits"><svg viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg></div>
              <div class="kpi-val">{{ stats.totalVisits }}</div>
              <div class="kpi-label">累计总访问量 (Visits)</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-icon articles"><svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" fill="currentColor"/></svg></div>
              <div class="kpi-val">{{ stats.counts.articles }}</div>
              <div class="kpi-label">知识库发布文章</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-icon projects"><svg viewBox="0 0 24 24"><path d="M4 6h16v12H4zM2 4v16h20V4H2zm9 5h2v6h-2z" fill="currentColor"/></svg></div>
              <div class="kpi-val">{{ stats.counts.projects }}</div>
              <div class="kpi-label">作品项目归档</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-icon pending"><svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" fill="currentColor"/></svg></div>
              <div class="kpi-val highlight">{{ (stats.pending.messages || 0) + (stats.pending.links || 0) }}</div>
              <div class="kpi-label">待审核留言与友链</div>
            </div>
          </div>

          <!-- 近30天访问趋势图 -->
          <div class="dashboard-chart-card card">
            <div class="card-head"><strong>近 30 天访客流量趋势分析</strong></div>
            <div ref="visitChartEl" style="height: 320px; width: 100%;"></div>
          </div>
        </section>

        <!-- ===== 2. 界面与快捷配置 (Layout & Quick Settings) ===== -->
        <section v-if="activeMenu === 'layout'" class="section-pane">
          <div class="config-grid">
            <!-- 外观与主题 -->
            <div class="config-card card">
              <h3>🎨 页面主题与全站 Accent 色</h3>
              <div class="form-row">
                <label>主题 Accent 色度</label>
                <div class="colors">
                  <span
                    v-for="c in accents"
                    :key="c"
                    class="swatch"
                    :style="{ background: c }"
                    :class="{ active: store.settings.theme?.accent === c }"
                    @click="store.settings.theme.accent = c; saveEffectsAndTheme()"
                  ></span>
                </div>
              </div>
              <div class="form-row">
                <label>3D 背景动画强度 (Intensity)</label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  v-model.number="store.settings.effects.intensity"
                  @change="saveEffectsAndTheme"
                />
                <span>{{ store.settings.effects.intensity }}</span>
              </div>
            </div>

            <!-- AI 助手快捷设置 -->
            <div class="config-card card">
              <h3>🤖 AI 悬浮助手设置</h3>
              <div class="form-row">
                <label>开启全站 AI 助手</label>
                <input
                  type="checkbox"
                  v-model="store.settings.ai.enabled"
                  @change="saveEffectsAndTheme"
                />
              </div>
              <div class="form-row">
                <label>默认欢迎语</label>
                <input
                  type="text"
                  class="input"
                  v-model="store.settings.ai.welcome"
                  @blur="saveEffectsAndTheme"
                />
              </div>
            </div>
          </div>

          <!-- 首页拖拽卡片 Layout 占比配置 -->
          <div class="card layout-panel" style="margin-top: 20px;">
            <h3>📐 首页模块比例 (Span Rows) 快捷调节</h3>
            <div class="layout-items">
              <div v-for="item in layoutConfig" :key="item.id" class="layout-item-row">
                <strong>{{ item.title }} (ID: {{ item.id }})</strong>
                <div class="span-btns">
                  <button
                    v-for="s in [3, 4, 6, 8, 12]"
                    :key="s"
                    class="btn btn-xs"
                    :class="{ 'btn-primary': item.span === s }"
                    @click="saveLayoutSpan(item.id, s)"
                  >
                    Span {{ s }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ===== 3. 留言风控审核 (Message Reviews) ===== -->
        <section v-if="activeMenu === 'messages'" class="section-pane">
          <div class="table-toolbar card">
            <div class="filters">
              <button
                v-for="st in [
                  { id: 'pending', label: '待审核' },
                  { id: 'approved', label: '已过审' },
                  { id: 'rejected', label: '已拦截' },
                  { id: 'all', label: '全部留言' }
                ]"
                :key="st.id"
                class="chip"
                :class="{ on: msgFilter === st.id }"
                @click="msgFilter = st.id"
              >
                {{ st.label }}
              </button>
            </div>
          </div>

          <div class="table-card card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>访客昵称</th>
                  <th>留言内容</th>
                  <th>状态</th>
                  <th>提交时间</th>
                  <th style="width: 220px;">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in filteredMessages" :key="m.id">
                  <td>#{{ m.id }}</td>
                  <td><strong>{{ m.nickname }}</strong></td>
                  <td class="msg-content-cell">{{ m.content }}</td>
                  <td>
                    <span class="status-tag" :class="m.status">{{ m.status }}</span>
                  </td>
                  <td><small>{{ fmtDate(m.created_at) }}</small></td>
                  <td>
                    <div class="btn-group">
                      <button v-if="m.status !== 'approved'" class="btn btn-xs btn-success" @click="reviewMsg(m, 'approve')">通过</button>
                      <button v-if="m.status !== 'rejected'" class="btn btn-xs btn-warn" @click="reviewMsg(m, 'reject')">拦截</button>
                      <button class="btn btn-xs" @click="reviewMsg(m, 'reply')">回复</button>
                      <button class="btn btn-xs btn-danger" @click="reviewMsg(m, 'delete')">删除</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- ===== 4. 友情链接审核 (Links) ===== -->
        <section v-if="activeMenu === 'links'" class="section-pane">
          <div class="table-card card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>站点名称</th>
                  <th>URL 网址</th>
                  <th>描述说明</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="l in links" :key="l.id">
                  <td><strong>{{ l.name }}</strong></td>
                  <td><a :href="l.url" target="_blank">{{ l.url }}</a></td>
                  <td>{{ l.description || '-' }}</td>
                  <td><span class="status-tag" :class="l.status">{{ l.status }}</span></td>
                  <td>
                    <div class="btn-group">
                      <button v-if="l.status !== 'approved'" class="btn btn-xs btn-success" @click="reviewLink(l, 'approved')">批准</button>
                      <button v-if="l.status !== 'rejected'" class="btn btn-xs btn-warn" @click="reviewLink(l, 'rejected')">拒绝</button>
                      <button class="btn btn-xs btn-danger" @click="delLink(l)">删除</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- ===== 5. 知识库文章管理 (Articles) ===== -->
        <section v-if="activeMenu === 'articles'" class="section-pane">
          <div class="table-card card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>文章标题</th>
                  <th>阅读量</th>
                  <th>标签</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in articles" :key="a.id">
                  <td><strong>{{ a.title }}</strong></td>
                  <td>{{ a.views }} 次</td>
                  <td><span v-for="t in a.tags" :key="t" class="tag">{{ t }}</span></td>
                  <td><small>{{ fmtDate(a.created_at) }}</small></td>
                  <td>
                    <button class="btn btn-xs btn-danger" @click="delArticle(a)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- ===== 6. 作品项目集 (Projects) ===== -->
        <section v-if="activeMenu === 'projects'" class="section-pane">
          <div class="table-card card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>项目名称</th>
                  <th>描述</th>
                  <th>精选推荐</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in projects" :key="p.id">
                  <td><strong>{{ p.title }}</strong></td>
                  <td>{{ p.description }}</td>
                  <td>
                    <button
                      class="btn btn-xs"
                      :class="p.featured ? 'btn-success' : 'btn-ghost'"
                      @click="toggleFeatured(p)"
                    >
                      {{ p.featured ? '★ 已推荐' : '☆ 普通' }}
                    </button>
                  </td>
                  <td>
                    <button class="btn btn-xs btn-danger" @click="api.del(`/projects/${p.id}`); reloadData()">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- ===== 7. 站长与系统设置 (Profile & Settings) ===== -->
        <section v-if="activeMenu === 'profile'" class="section-pane">
          <div v-if="profile" class="card profile-form">
            <h3>👤 站长基本资料配置</h3>
            <div class="form-grid">
              <div class="form-group">
                <label>姓名</label>
                <input v-model="profile.name" class="input" />
              </div>
              <div class="form-group">
                <label>头衔 / 职业</label>
                <input v-model="profile.title" class="input" />
              </div>
              <div class="form-group">
                <label>城市位置</label>
                <input v-model="profile.location" class="input" />
              </div>
              <div class="form-group">
                <label>联系邮箱</label>
                <input v-model="profile.email" class="input" />
              </div>
              <div class="form-group full">
                <label>座右铭 / 签名</label>
                <input v-model="profile.motto" class="input" />
              </div>
              <div class="form-group full">
                <label>个人简介 (Bio)</label>
                <textarea v-model="profile.bio" class="input" rows="4"></textarea>
              </div>
            </div>
            <button class="btn btn-primary" style="margin-top: 16px;" @click="saveProfile">保存资料</button>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* 后台管理系统主布局 */
.admin-console-wrap {
  display: flex;
  min-height: 100vh;
  background: #0B0E14;
  color: #E6E8EC;
  font-family: var(--font-sans);
}

/* 左侧纵向 Sidebar */
.admin-sidebar {
  width: 240px;
  background: #12161F;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease;
  flex: none;
  z-index: 50;
}
.admin-sidebar.collapsed {
  width: 68px;
}

.sidebar-head {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
}
.sidebar-logo i {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--accent);
  display: block;
}
.sidebar-logo b {
  color: var(--accent);
  margin-left: 2px;
}
.toggle-btn {
  background: none;
  border: none;
  color: #8C9099;
  cursor: pointer;
  padding: 4px;
}
.toggle-btn svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nav-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: #9A9FA9;
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  text-align: left;
}
.nav-btn svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
  flex: none;
}
.nav-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #FFFFFF;
}
.nav-btn.active {
  background: var(--accent);
  color: #FFFFFF;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(228, 87, 46, 0.35);
}

.badge {
  background: #E4572E;
  color: #FFF;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 99px;
  margin-left: auto;
  font-style: normal;
}

.sidebar-foot {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.admin-profile {
  display: flex;
  align-items: center;
  gap: 10px;
}
.admin-profile .avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent);
  color: #FFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
}
.admin-profile .info strong {
  display: block;
  font-size: 13px;
  color: #FFF;
}
.admin-profile .info small {
  color: #7A7F8D;
  font-size: 11px;
}
.logout-icon-btn {
  background: none;
  border: none;
  color: #8C9099;
  cursor: pointer;
}
.logout-icon-btn:hover {
  color: #E4572E;
}

/* 右侧 Main Workspace */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #0B0E14;
}

.admin-header {
  height: 64px;
  padding: 0 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #12161F;
}
.breadcrumb {
  font-size: 14px;
}
.breadcrumb .muted {
  color: #8C9099;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-body {
  padding: 28px;
  flex: 1;
  overflow-y: auto;
}

/* 仪表盘 KPI Cards */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.kpi-card {
  background: #161B26;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}
.kpi-icon svg {
  width: 20px;
  height: 20px;
}
.kpi-icon.visits { background: rgba(46, 134, 171, 0.15); color: #2E86AB; }
.kpi-icon.articles { background: rgba(61, 122, 94, 0.15); color: #3D7A5E; }
.kpi-icon.projects { background: rgba(217, 147, 44, 0.15); color: #D9932C; }
.kpi-icon.pending { background: rgba(228, 87, 46, 0.15); color: #E4572E; }

.kpi-val {
  font-size: 26px;
  font-weight: 700;
  color: #FFF;
}
.kpi-val.highlight {
  color: var(--accent);
}
.kpi-label {
  font-size: 12px;
  color: #8C9099;
}

.dashboard-chart-card {
  background: #161B26;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  padding: 20px;
}
.card-head {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}

/* 页面配置网格 */
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}
.config-card {
  background: #161B26;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  padding: 22px;
}
.config-card h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 18px;
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 13.5px;
}
.colors {
  display: flex;
  gap: 8px;
}
.swatch {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}
.swatch.active {
  transform: scale(1.25);
  box-shadow: 0 0 0 2px #FFF;
}

.layout-panel {
  background: #161B26;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  padding: 22px;
}
.layout-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
}
.layout-item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

/* 表格卡片样式 */
.table-card {
  background: #161B26;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  overflow: hidden;
}
.table-toolbar {
  background: #161B26;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  padding: 14px 20px;
  margin-bottom: 16px;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}
.data-table th {
  background: rgba(255, 255, 255, 0.03);
  color: #8C9099;
  font-weight: 500;
  text-align: left;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: #D1D5DB;
}
.msg-content-cell {
  max-width: 360px;
  word-break: break-word;
}
.status-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 99px;
  text-transform: uppercase;
}
.status-tag.approved { background: rgba(61, 122, 94, 0.2); color: #4ADE80; }
.status-tag.pending { background: rgba(228, 87, 46, 0.2); color: #FB923C; }
.status-tag.rejected { background: rgba(239, 68, 68, 0.2); color: #F87171; }

.btn-group {
  display: flex;
  gap: 6px;
}
.btn-xs {
  font-size: 11.5px;
  padding: 4px 8px;
}

/* 个人资料表单 */
.profile-form {
  background: #161B26;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  padding: 24px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 16px;
}
.form-group.full {
  grid-column: span 2;
}
.form-group label {
  display: block;
  font-size: 12.5px;
  color: #8C9099;
  margin-bottom: 6px;
}

@media (max-width: 860px) {
  .admin-sidebar {
    width: 68px;
  }
  .admin-sidebar .sidebar-logo span, .admin-sidebar .nav-btn span, .admin-sidebar .sidebar-foot {
    display: none;
  }
  .admin-header {
    padding: 0 16px;
  }
  .admin-body {
    padding: 16px;
  }
}
</style>
