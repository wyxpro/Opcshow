<script setup lang="ts">
/** 首页 · 个人总览：3D 背景 Hero + 可拖拽组件网格（PRD P0：可视化拖拽自定义） */
import Sortable from 'sortablejs'
import { computed, nextTick, onMounted, ref } from 'vue'
import { api, isAdmin, type Interest, type LayoutItem, type Profile, type Project, type Skill } from '../api'
import Carousel from '../components/Carousel.vue'
import ShareCard from '../components/ShareCard.vue'
import ThreeBg from '../components/ThreeBg.vue'
import { useChart } from '../components/useChart'
import { store, toast } from '../store'

const profile = ref<Profile | null>(null)
const skills = ref<Skill[]>([])
const projects = ref<Project[]>([])
const interests = ref<Interest[]>([])
const layout = ref<LayoutItem[]>([])
const editMode = ref(false)
const shareOpen = ref(false)
const gridEl = ref<HTMLElement | null>(null)
const radarEl = ref<HTMLElement | null>(null)
let sortable: Sortable | null = null

const featured = computed(() => projects.value.filter(p => p.featured))
const threeOn = computed(() => store.settings.effects?.three !== false)

/* 技能雷达图（ECharts） */
useChart(radarEl, () => ({
  radar: {
    indicator: skills.value.slice(0, 6).map(s => ({ name: s.name, max: 100 })),
    radius: '68%', splitNumber: 4,
    axisName: { color: '#4E535B', fontSize: 12 },
    splitArea: { areaStyle: { color: ['#FBFAF6', '#F6F4EE', '#FBFAF6', '#F1EDE3'] } },
    splitLine: { lineStyle: { color: '#E6E1D5' } },
    axisLine: { lineStyle: { color: '#E6E1D5' } },
  },
  series: [{
    type: 'radar',
    data: [{
      value: skills.value.slice(0, 6).map(s => s.level), name: '技能水平',
      areaStyle: { color: 'rgba(228, 87, 46, .22)' },
      lineStyle: { color: '#E4572E', width: 2.5 },
      itemStyle: { color: '#E4572E' },
      symbolSize: 5,
    }],
    animationDuration: 900,
  }],
}))

const sectionMap: Record<string, any> = {
  profile: { comp: 'profile' }, skills: { comp: 'skills' }, works: { comp: 'works' },
  interests: { comp: 'interests' }, stats: { comp: 'stats' },
}

async function load() {
  const [p, s, pr, it, lo] = await Promise.all([
    api.get('/profile'), api.get('/skills'), api.get('/projects'),
    api.get('/interests'), api.get('/layout'),
  ])
  profile.value = p; skills.value = s; projects.value = pr; interests.value = it
  layout.value = lo?.config?.length ? lo.config : [
    { id: 'profile', title: '个人资料', span: 4 },
    { id: 'skills', title: '技能雷达', span: 4 },
    { id: 'works', title: '作品集', span: 4 },
    { id: 'interests', title: '兴趣爱好', span: 6 },
    { id: 'stats', title: '数据概览', span: 6 },
  ]
}

function toggleEdit() {
  editMode.value = !editMode.value
  nextTick(() => {
    if (editMode.value && gridEl.value && !sortable) {
      sortable = new Sortable(gridEl.value, {
        animation: 240,
        handle: '.drag-handle',
        ghostClass: 'drag-ghost',
        onEnd: (e) => {
          if (e.oldIndex === undefined || e.newIndex === undefined) return
          const moved = layout.value.splice(e.oldIndex, 1)[0]
          layout.value.splice(e.newIndex, 0, moved)
        },
      })
    } else if (!editMode.value) {
      sortable?.destroy(); sortable = null
    }
  })
}

async function saveLayout() {
  // 同步 DOM 顺序到数据
  if (gridEl.value) {
    const ids = Array.from(gridEl.value.children).map(el => (el as HTMLElement).dataset.sec)
    layout.value.sort((a, b) => ids.indexOf(a.id) - ids.indexOf(b.id))
  }
  await api.put('/layout', { config: layout.value })
  toast('布局已保存', 'ok')
  toggleEdit()
}

function grow(item: LayoutItem, delta: number) {
  item.span = Math.min(12, Math.max(3, item.span + delta))
}

onMounted(load)
</script>

<template>
  <div class="home">
    <!-- ======== Hero：3D 动态背景 ======== -->
    <section class="hero card">
      <ThreeBg v-if="threeOn" :intensity="store.settings.effects?.intensity ?? 0.6" />
      <div class="hero-inner">
        <div class="hero-text">
          <span class="hero-hi">你好，我是</span>
          <h1>{{ profile?.name || '林一舟' }}</h1>
          <p class="hero-title">{{ profile?.title }}</p>
          <p class="hero-motto">「 {{ profile?.motto }} 」</p>
          <div class="hero-actions">
            <button class="btn btn-primary" @click="shareOpen = true">分享主页</button>
            <router-link to="/work/knowledge" class="btn btn-dark">进入知识库</router-link>
          </div>
        </div>
        <div class="hero-avatar">
          <div class="avatar-ring"><span>{{ (profile?.name || '舟').slice(-1) }}</span></div>
        </div>
      </div>
      <div class="hero-scroll"><i></i></div>
    </section>

    <!-- ======== 编辑工具条 ======== -->
    <div class="edit-bar card">
      <div class="edit-info">
        <strong>主页组件</strong>
        <small>{{ editMode ? '拖拽手柄排序，加减调整宽度，保存后生效' : '自定义你的主页布局' }}</small>
      </div>
      <div class="edit-ops">
        <template v-if="editMode">
          <button class="btn btn-ghost btn-sm" @click="toggleEdit">取消</button>
          <button class="btn btn-primary btn-sm" @click="saveLayout">保存布局</button>
        </template>
        <button v-else-if="isAdmin()" class="btn btn-ghost btn-sm" @click="toggleEdit">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 8h10M18 8h2M4 16h2M10 16h10M14 5v6M7 13v6"/></svg>
          自定义布局
        </button>
      </div>
    </div>

    <!-- ======== 可拖拽组件网格 ======== -->
    <div ref="gridEl" class="grid" :class="{ editing: editMode }">
      <section v-for="item in layout" :key="item.id" :data-sec="item.id"
               class="g-item" :style="{ gridColumn: `span ${item.span}` }">
        <!-- 拖拽手柄 -->
        <div v-if="editMode" class="drag-handle">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><circle cx="8" cy="6" r="1.6"/><circle cx="16" cy="6" r="1.6"/><circle cx="8" cy="12" r="1.6"/><circle cx="16" cy="12" r="1.6"/><circle cx="8" cy="18" r="1.6"/><circle cx="16" cy="18" r="1.6"/></svg>
          <span>{{ item.title }}</span>
          <div class="span-ops">
            <button @click="grow(item, -1)">−</button><em>{{ item.span }}/12</em><button @click="grow(item, 1)">＋</button>
          </div>
        </div>

        <!-- 个人资料卡 -->
        <div v-if="item.id === 'profile'" class="card hoverable panel profile-panel">
          <div class="panel-head"><h3>关于我</h3><span class="tag hot">{{ profile?.location }}</span></div>
          <p class="bio">{{ profile?.bio }}</p>
          <div class="p-tags">
            <span v-for="t in profile?.tags" :key="t" class="chip">{{ t }}</span>
          </div>
          <div class="p-foot">
            <span class="mail">✉ {{ profile?.email }}</span>
          </div>
        </div>

        <!-- 技能雷达 -->
        <div v-else-if="item.id === 'skills'" class="card hoverable panel">
          <div class="panel-head"><h3>技能雷达</h3><span class="tag">技术栈</span></div>
          <div ref="radarEl" class="radar"></div>
        </div>

        <!-- 作品轮播 -->
        <div v-else-if="item.id === 'works'" class="card hoverable panel">
          <div class="panel-head"><h3>精选作品</h3><router-link to="/work/knowledge" class="more">更多 →</router-link></div>
          <Carousel :items="featured.length ? featured : projects" :interval="store.settings.carousel?.interval ?? 4" />
        </div>

        <!-- 兴趣爱好 -->
        <div v-else-if="item.id === 'interests'" class="card hoverable panel">
          <div class="panel-head"><h3>兴趣爱好</h3><span class="tag warm">{{ interests.length }} 项</span></div>
          <div class="interest-grid">
            <div v-for="it in interests" :key="it.id" class="interest">
              <span class="i-icon">{{ it.icon }}</span>
              <div><strong>{{ it.name }}</strong><p>{{ it.description }}</p></div>
            </div>
          </div>
        </div>

        <!-- 数据概览 -->
        <div v-else-if="item.id === 'stats'" class="card hoverable panel">
          <div class="panel-head"><h3>数据概览</h3><span class="tag">实时</span></div>
          <div class="stat-grid">
            <div class="stat"><b>{{ projects.length }}</b><span>作品项目</span></div>
            <div class="stat"><b>{{ skills.length }}</b><span>技能标签</span></div>
            <div class="stat"><b>{{ interests.length }}</b><span>兴趣爱好</span></div>
            <div class="stat"><b>365</b><span>连续记录(天)</span></div>
          </div>
        </div>
      </section>
    </div>

    <ShareCard v-if="shareOpen" target="home" @close="shareOpen = false" />
  </div>
</template>

<style scoped>
.hero {
  position: relative; overflow: hidden; border-radius: var(--radius-lg);
  background: linear-gradient(135deg, #FBF9F3 0%, #F4EFE4 55%, #EFE9DB 100%);
  min-height: 320px; margin-bottom: 16px;
}
.hero-inner {
  position: relative; z-index: 2; display: flex; align-items: center; justify-content: space-between;
  gap: 24px; padding: 52px 48px; pointer-events: none;
}
.hero-inner .btn, .hero-inner a { pointer-events: auto; }
.hero-hi {
  display: inline-block; font-size: 13px; color: var(--accent-strong); font-weight: 600;
  background: var(--accent-soft); padding: 4px 14px; border-radius: 999px; margin-bottom: 14px;
  animation: slideUp .6s var(--ease) both;
}
.hero h1 { font-size: 46px; font-weight: 800; letter-spacing: .02em; animation: slideUp .6s .08s var(--ease) both; }
.hero-title { color: var(--ink-2); font-size: 17px; margin-top: 6px; animation: slideUp .6s .16s var(--ease) both; }
.hero-motto { color: var(--muted); font-size: 14px; margin-top: 12px; animation: slideUp .6s .24s var(--ease) both; }
.hero-actions { display: flex; gap: 12px; margin-top: 26px; animation: slideUp .6s .32s var(--ease) both; }

.hero-avatar { animation: slideUp .7s .2s var(--ease) both; }
.avatar-ring {
  width: 132px; height: 132px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--amber));
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 18px 40px -12px rgba(228, 87, 46, .45);
  animation: floatY 5s ease-in-out infinite;
  position: relative;
}
.avatar-ring::before {
  content: ''; position: absolute; inset: -10px; border-radius: 50%;
  border: 2px dashed rgba(228, 87, 46, .35); animation: spin 24s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg) } }
.avatar-ring span { font-size: 46px; color: #FFF7EE; font-weight: 700; }

.hero-scroll { position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%); z-index: 2; }
.hero-scroll i { display: block; width: 22px; height: 34px; border: 2px solid var(--muted); border-radius: 12px; position: relative; opacity: .5; }
.hero-scroll i::after { content: ''; position: absolute; left: 50%; top: 6px; width: 3px; height: 7px; margin-left: -1.5px; border-radius: 3px; background: var(--muted); animation: wheel 1.6s infinite; }
@keyframes wheel { 0% { transform: translateY(0); opacity: 1 } 70% { transform: translateY(10px); opacity: 0 } 100% { opacity: 0 } }

.edit-bar { display: flex; align-items: center; justify-content: space-between; padding: 12px 18px; margin-bottom: 16px; }
.edit-info strong { font-size: 14.5px; margin-right: 10px; }
.edit-info small { color: var(--muted); font-size: 12.5px; }

.grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }
.g-item { position: relative; min-width: 0; }
.panel { padding: 20px; height: 100%; }
.panel-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.panel-head h3 { font-size: 16px; font-weight: 600; }
.more { font-size: 13px; color: var(--muted); transition: color .2s; }
.more:hover { color: var(--accent); }

.profile-panel .bio { color: var(--ink-2); font-size: 14px; line-height: 1.8; }
.p-tags { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 14px; }
.p-foot { margin-top: 14px; padding-top: 12px; border-top: 1px dashed var(--line); }
.mail { font-size: 13px; color: var(--muted); }

.radar { width: 100%; height: 250px; }

.interest-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 12px; }
.interest {
  display: flex; gap: 11px; padding: 12px; border-radius: 12px; background: var(--surface-2);
  border: 1px solid var(--line-2); transition: all .25s var(--ease);
}
.interest:hover { border-color: var(--accent); transform: translateY(-2px); box-shadow: var(--shadow); }
.i-icon {
  width: 34px; height: 34px; border-radius: 10px; flex: none;
  background: var(--accent-soft); color: var(--accent-strong);
  display: flex; align-items: center; justify-content: center; font-size: 16px;
}
.interest strong { font-size: 14px; display: block; }
.interest p { font-size: 12px; color: var(--muted); line-height: 1.5; margin-top: 2px; }

.stat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.stat {
  padding: 16px; border-radius: 12px; text-align: center;
  background: linear-gradient(160deg, var(--surface-2), var(--bg));
  border: 1px solid var(--line-2);
}
.stat b { font-size: 26px; font-weight: 800; color: var(--accent); display: block; }
.stat span { font-size: 12px; color: var(--muted); }

/* 编辑态 */
.grid.editing .g-item { cursor: default; }
.grid.editing .panel { opacity: .45; pointer-events: none; }
.drag-handle {
  position: absolute; inset: 0; z-index: 5; border-radius: var(--radius);
  border: 2px dashed var(--accent); background: rgba(251, 233, 226, .55);
  display: flex; align-items: center; justify-content: center; gap: 8px;
  color: var(--accent-strong); font-weight: 600; font-size: 14px; cursor: grab;
  backdrop-filter: blur(1px);
}
.drag-handle:active { cursor: grabbing; }
.drag-ghost { opacity: .35; }
.span-ops { position: absolute; bottom: 10px; right: 12px; display: flex; align-items: center; gap: 6px; }
.span-ops button {
  width: 26px; height: 26px; border-radius: 8px; background: var(--ink); color: #F5F2EA;
  font-size: 15px; line-height: 1;
}
.span-ops em { font-style: normal; font-size: 12px; color: var(--ink-2); }

@media (max-width: 1080px) {
  .g-item { grid-column: span 6 !important; }
}
@media (max-width: 860px) {
  .hero-inner { flex-direction: column-reverse; text-align: center; padding: 36px 22px 60px; }
  .hero h1 { font-size: 34px; }
  .hero-actions { justify-content: center; }
  .avatar-ring { width: 96px; height: 96px; }
  .avatar-ring span { font-size: 34px; }
  .g-item { grid-column: span 12 !important; }
  .hero-scroll { display: none; }
  .edit-info small { display: block; }
}
</style>
