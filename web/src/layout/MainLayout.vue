<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isAdmin, setToken } from '../api'
import { loadSettings, store } from '../store'
import AiAssistant from '../components/AiAssistant.vue'

const route = useRoute()
const router = useRouter()
const mobileNavOpen = ref(false)

// 当前展开的顶部下拉菜单 key
const activeDropdown = ref<string | null>(null)
let closeTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  loadSettings()
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})

function handleOutsideClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.nav-group-wrapper')) {
    activeDropdown.value = null
  }
}

interface NavItem { name: string; path: string; icon: string }
interface NavGroup { key: string; label: string; icon: string; children?: NavItem[]; path?: string }

const nav: NavGroup[] = [
  { key: 'home', label: '首页', icon: 'M3 11.5 12 4l9 7.5M5 10v10h5v-6h4v6h5V10', path: '/' },
  {
    key: 'work', label: '工作', icon: 'M4 7h16v13H4zM9 7V4h6v3M4 12h16',
    children: [
      { name: '知识库', path: '/work/knowledge', icon: 'M4 5h7v15H4zM13 5h7v15h-7zM6.5 9h2M6.5 12h2M15.5 9h2M15.5 12h2' },
      { name: '在线简历', path: '/work/resume', icon: 'M7 3h10v18H7zM10 8h4M10 12h4M10 16h2' },
    ],
  },
  {
    key: 'life', label: '生活', icon: 'M12 21s-7.5-4.6-9.3-9A5.4 5.4 0 0 1 12 6.6 5.4 5.4 0 0 1 21.3 12c-1.8 4.4-9.3 9-9.3 9z',
    children: [
      { name: '朋友圈', path: '/life/moments', icon: 'M4 5h16v12H8l-4 4z' },
      { name: '恋爱记录', path: '/life/love', icon: 'M12 20s-6-3.8-7.5-7.2A4.3 4.3 0 0 1 12 7a4.3 4.3 0 0 1 7.5 5.8C18 16.2 12 20 12 20z' },
      { name: '旅拍地图', path: '/life/travel', icon: 'M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2zM9 4v14M15 6v14' },
      { name: '运动数据', path: '/life/sports', icon: 'M4 14c2 0 2-4 4-4s2 8 4 8 2-10 4-10 2 6 4 6' },
      { name: '游戏档案', path: '/life/games', icon: 'M7 8h10a5 5 0 0 1 5 5v3l-3-2H5L2 16v-3a5 5 0 0 1 5-5zM8 11v4M6 13h4' },
    ],
  },
  {
    key: 'fun', label: '娱乐', icon: 'M9 18V6l11-2v12M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM20 16a3 3 0 1 1-6 0 3 3 0 0 1 6 0z',
    children: [
      { name: '音乐盒', path: '/fun/music', icon: 'M9 18V6l11-2v12M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0z' },
      { name: '电影收藏', path: '/fun/movies', icon: 'M4 5h16v14H4zM4 9h16M8 5v4M16 5v4' },
      { name: '百宝箱', path: '/fun/box', icon: 'M4 8h16v12H4zM4 8l2-4h12l2 4M12 12v4' },
    ],
  },
  {
    key: 'me', label: '我的', icon: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5',
    children: [
      { name: '友情链接', path: '/me/links', icon: 'M10 14a4 4 0 0 0 6 0l3-3a4 4 0 1 0-6-5l-1 1M14 10a4 4 0 0 0-6 0l-3 3a4 4 0 1 0 6 5l1-1' },
      { name: '留言弹幕', path: '/me/messages', icon: 'M3 6h18M3 12h12M3 18h15' },
      { name: '成长时间轴', path: '/me/timeline', icon: 'M12 8v5l3 2M12 21a9 9 0 1 1 0-18 9 9 0 0 1 0 18z' },
      { name: '自媒体矩阵', path: '/me/matrix', icon: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z' },
    ],
  },
  { key: 'admin', label: '后台管理', icon: 'M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7zM9 12l2 2 4-4', path: '/admin' },
]

const activeGroup = computed(() => (route.meta.group as string) || 'home')

function go(path: string) {
  mobileNavOpen.value = false
  activeDropdown.value = null
  router.push(path)
}

function handleMenuClick(g: NavGroup) {
  if (g.path) {
    activeDropdown.value = null
    go(g.path)
    return
  }
  // 点击含子菜单的主项：点击展开/切换子菜单，默认跳转到首项
  if (activeDropdown.value === g.key) {
    activeDropdown.value = null
  } else {
    activeDropdown.value = g.key
    if (g.children && g.children.length > 0) {
      go(g.children[0].path)
      activeDropdown.value = g.key
    }
  }
}

function onMenuMouseEnter(g: NavGroup) {
  if (closeTimer) clearTimeout(closeTimer)
  if (g.children && g.children.length > 0) {
    activeDropdown.value = g.key
  }
}

function onMenuMouseLeave() {
  closeTimer = setTimeout(() => {
    activeDropdown.value = null
  }, 200)
}

function logout() {
  setToken('')
  router.push('/')
}

// 移动端底部主导航（5 项）
const tabbar = [
  { key: 'home', label: '首页', path: '/', icon: 'M3 11.5 12 4l9 7.5M5 10v10h5v-6h4v6h5V10' },
  { key: 'work', label: '工作', path: '/work/knowledge', icon: 'M4 7h16v13H4zM9 7V4h6v3' },
  { key: 'life', label: '生活', path: '/life/moments', icon: 'M12 21s-7.5-4.6-9.3-9A5.4 5.4 0 0 1 12 6.6 5.4 5.4 0 0 1 21.3 12c-1.8 4.4-9.3 9-9.3 9z' },
  { key: 'fun', label: '娱乐', path: '/fun/music', icon: 'M9 18V6l11-2v12M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0z' },
  { key: 'me', label: '我的', path: '/me/links', icon: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5' },
]
</script>

<template>
  <div class="app-shell">
    <!-- ======== PC 顶部导航栏 ======== -->
    <header class="pc-topnav">
      <div class="topnav-container">
        <!-- 品牌 / Logo -->
        <div class="brand" @click="go('/')">
          <span class="brand-logo"><i></i></span>
          <div class="brand-text">
            <strong>{{ store.settings.site?.name || 'Opcshow' }}</strong>
            <small>{{ store.settings.site?.subtitle || '个人动态主页' }}</small>
          </div>
        </div>

        <!-- 顶部主导航菜单 -->
        <nav class="topnav-menu">
          <div
            v-for="g in nav"
            :key="g.key"
            class="nav-group-wrapper"
            @mouseenter="onMenuMouseEnter(g)"
            @mouseleave="onMenuMouseLeave"
          >
            <!-- 菜单按键 -->
            <button
              class="nav-item-btn"
              :class="{ on: activeGroup === g.key || activeDropdown === g.key }"
              @click="handleMenuClick(g)"
            >
              <svg viewBox="0 0 24 24"><path :d="g.icon" /></svg>
              <span>{{ g.label }}</span>
              <svg v-if="g.children" class="caret" :class="{ open: activeDropdown === g.key }" viewBox="0 0 24 24">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>

            <!-- 子菜单下拉面板（丝滑过度） -->
            <transition name="dropdown">
              <div v-if="g.children && activeDropdown === g.key" class="dropdown-panel">
                <div class="dropdown-list">
                  <a
                    v-for="c in g.children"
                    :key="c.path"
                    class="dropdown-item"
                    :class="{ on: route.path === c.path }"
                    @click.stop="go(c.path)"
                  >
                    <svg viewBox="0 0 24 24"><path :d="c.icon" /></svg>
                    <span>{{ c.name }}</span>
                  </a>
                </div>
              </div>
            </transition>
          </div>
        </nav>

        <!-- 右侧用户状态与登录按钮 -->
        <div class="topnav-foot">
          <template v-if="isAdmin()">
            <div class="me-chip">
              <span class="me-avatar">舟</span>
              <div class="me-info"><strong>林一舟</strong><small>管理员</small></div>
            </div>
            <button class="logout-btn" @click="logout">退出登录</button>
          </template>
          <button v-else class="login-btn" @click="go('/login')">站长登录</button>
        </div>
      </div>
    </header>

    <!-- ======== 移动端顶栏 ======== -->
    <header class="mobile-top">
      <button class="hamburger" @click="mobileNavOpen = true" aria-label="菜单">
        <svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h10" /></svg>
      </button>
      <strong>{{ route.meta.title || 'Opcshow' }}</strong>
      <span style="width:36px"></span>
    </header>

    <!-- 移动端抽屉菜单 -->
    <transition name="fade">
      <div v-if="mobileNavOpen" class="drawer-mask" @click="mobileNavOpen = false">
        <aside class="drawer" @click.stop>
          <div class="brand" @click="go('/')">
            <span class="brand-logo"><i></i></span>
            <div><strong>Opcshow</strong><small>个人动态主页</small></div>
          </div>
          <nav class="side-nav">
            <template v-for="g in nav" :key="g.key">
              <a v-if="!g.children" class="nav-item" :class="{ on: activeGroup === g.key }" @click="go(g.path!)">
                <svg viewBox="0 0 24 24"><path :d="g.icon" /></svg><span>{{ g.label }}</span>
              </a>
              <div v-else class="nav-group">
                <div class="drawer-group-label">{{ g.label }}</div>
                <a v-for="c in g.children" :key="c.path" class="sub-item" :class="{ on: route.path === c.path }" @click="go(c.path)">
                  <svg viewBox="0 0 24 24"><path :d="c.icon" /></svg><span>{{ c.name }}</span>
                </a>
              </div>
            </template>
          </nav>
        </aside>
      </div>
    </transition>

    <!-- ======== 主内容 ======== -->
    <main class="main-area">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>

    <!-- ======== 移动端底部 TabBar ======== -->
    <nav class="tabbar">
      <a v-for="t in tabbar" :key="t.key" :class="{ on: activeGroup === t.key }" @click="go(t.path)">
        <svg viewBox="0 0 24 24"><path :d="t.icon" /></svg>
        <span>{{ t.label }}</span>
      </a>
    </nav>

    <!-- 全局悬浮 AI 助手 -->
    <AiAssistant v-if="store.settings.ai?.enabled !== false" />

    <!-- Toast -->
    <div class="toast-wrap">
      <div v-for="t in store.toasts" :key="t.id" class="toast" :class="t.kind">{{ t.text }}</div>
    </div>
  </div>
</template>

<style scoped>
/* ---------- PC 顶部导航栏 ---------- */
.pc-topnav {
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
  background: rgba(255, 253, 248, 0.88);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--line-2);
  box-shadow: 0 4px 20px -6px rgba(35, 38, 43, 0.05);
}

.topnav-container {
  max-width: 1280px;
  height: 64px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s var(--ease);
}
.brand:hover {
  opacity: 0.85;
}
.brand-logo {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
  box-shadow: 0 4px 12px -3px rgba(228, 87, 46, 0.4);
}
.brand-logo i {
  width: 13px;
  height: 13px;
  border: 3px solid #FFF5EC;
  border-radius: 50%;
}
.brand-text strong {
  display: block;
  color: var(--ink);
  font-size: 16px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: .01em;
}
.brand-text small {
  color: var(--muted);
  font-size: 11px;
  line-height: 1;
}

/* 顶部菜单 */
.topnav-menu {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-group-wrapper {
  position: relative;
}

.nav-item-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 14.5px;
  font-weight: 500;
  color: var(--ink-2);
  cursor: pointer;
  background: transparent;
  transition: all 0.22s var(--ease);
  user-select: none;
}
.nav-item-btn svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex: none;
}
.nav-item-btn .caret {
  width: 14px;
  height: 14px;
  margin-left: 2px;
  transition: transform 0.25s var(--ease);
  opacity: 0.6;
}
.nav-item-btn .caret.open {
  transform: rotate(180deg);
  opacity: 1;
}

.nav-item-btn:hover {
  background: var(--bg-deep);
  color: var(--ink);
}
.nav-item-btn.on {
  background: var(--accent);
  color: #FFF5EC;
  font-weight: 600;
  box-shadow: 0 4px 14px -4px rgba(228, 87, 46, 0.5);
}

/* 下拉菜单面板 */
.dropdown-panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  min-width: 170px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--line-2);
  border-radius: 16px;
  box-shadow: 0 14px 38px -8px rgba(35, 38, 43, 0.14), 0 4px 12px -2px rgba(35, 38, 43, 0.06);
  padding: 6px;
  transform-origin: top center;
}

.dropdown-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border-radius: 10px;
  font-size: 13.5px;
  color: var(--ink-2);
  cursor: pointer;
  transition: all 0.2s var(--ease);
  white-space: nowrap;
}
.dropdown-item svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.dropdown-item:hover {
  background: var(--accent-soft);
  color: var(--accent-strong);
  transform: translateX(3px);
}
.dropdown-item.on {
  background: var(--accent);
  color: #FFF5EC;
  font-weight: 600;
}

/* 下拉动画 */
.dropdown-enter-active {
  transition: opacity 0.24s var(--ease), transform 0.24s var(--ease-spring);
}
.dropdown-leave-active {
  transition: opacity 0.16s var(--ease), transform 0.16s var(--ease);
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(8px) scale(0.94);
}

/* 右侧用户/登录 */
.topnav-foot {
  display: flex;
  align-items: center;
  gap: 12px;
}
.me-chip {
  display: flex;
  align-items: center;
  gap: 8px;
}
.me-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--amber));
  color: #FFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}
.me-info strong {
  display: block;
  color: var(--ink);
  font-size: 13px;
  line-height: 1.2;
}
.me-info small {
  color: var(--muted);
  font-size: 11px;
}
.logout-btn {
  font-size: 12.5px;
  color: var(--muted);
  padding: 4px 10px;
  border-radius: 8px;
  transition: all 0.2s;
}
.logout-btn:hover {
  color: var(--accent);
  background: var(--accent-soft);
}
.login-btn {
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink-2);
  transition: all 0.2s var(--ease);
}
.login-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-soft);
}

/* ---------- 移动端 ---------- */
.mobile-top {
  display: none; position: fixed; top: 0; left: 0; right: 0; z-index: 90;
  background: rgba(246, 244, 238, .86); backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--line-2);
  padding: 10px 16px; align-items: center; justify-content: space-between;
}
.mobile-top strong { font-size: 16px; }
.hamburger { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; }
.hamburger svg { width: 22px; height: 22px; fill: none; stroke: var(--ink); stroke-width: 1.8; stroke-linecap: round; }

.drawer-mask { position: fixed; inset: 0; background: rgba(28, 26, 22, .4); z-index: 300; }
.drawer {
  position: absolute; left: 0; top: 0; bottom: 0; width: 272px;
  background: var(--sidebar); color: var(--sidebar-ink);
  overflow-y: auto; animation: slideL .32s var(--ease); padding-bottom: 30px;
}
@keyframes slideL { from { transform: translateX(-100%) } }
.drawer-group-label { padding: 14px 20px 4px; font-size: 12px; color: #6E727B; letter-spacing: .1em; }
.fade-enter-active, .fade-leave-active { transition: opacity .25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.tabbar {
  display: none; position: fixed; bottom: 0; left: 0; right: 0; z-index: 90;
  background: rgba(255, 255, 255, .92); backdrop-filter: blur(14px);
  border-top: 1px solid var(--line-2); padding: 6px 4px calc(6px + env(safe-area-inset-bottom));
}
.tabbar a {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px;
  font-size: 11px; color: var(--muted); padding: 4px 0; cursor: pointer;
  transition: color .2s;
}
.tabbar a svg { width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.tabbar a.on { color: var(--accent); font-weight: 600; }

@media (max-width: 860px) {
  .pc-topnav { display: none; }
  .mobile-top { display: flex; }
  .tabbar { display: flex; }
  .main-area { padding-top: 66px !important; }
}
</style>

