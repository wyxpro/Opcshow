<script setup lang="ts">
/** 后台管理：数据统计 / 留言审核 / 友链审核 / 组件与外观配置（PRD P0 后台基础管理系统） */
import { onMounted, ref } from 'vue'
import { api, fromNow } from '../api'
import { useChart } from '../components/useChart'
import { applyAccent, store, toast } from '../store'

const tab = ref('dashboard')
const stats = ref<any>(null)
const allMessages = ref<any[]>([])
const allLinks = ref<any[]>([])
const visitEl = ref<HTMLElement | null>(null)

const tabs = [
  { id: 'dashboard', name: '数据总览' },
  { id: 'review', name: '留言审核' },
  { id: 'links', name: '友链管理' },
  { id: 'settings', name: '组件与外观' },
]

useChart(visitEl, () => ({
  grid: { left: 44, right: 16, top: 26, bottom: 26 },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category', data: (stats.value?.visits || []).map((v: any) => v.visit_date.slice(5)),
    axisLabel: { color: '#8C9099', fontSize: 10 }, axisLine: { lineStyle: { color: '#E6E1D5' } },
  },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#F0EBE0' } }, axisLabel: { color: '#8C9099', fontSize: 11 } },
  series: [{
    type: 'line', smooth: true, symbol: 'none',
    data: (stats.value?.visits || []).map((v: any) => v.count),
    lineStyle: { color: '#E4572E', width: 2.5 },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(228,87,46,.28)' }, { offset: 1, color: 'rgba(228,87,46,0)' }] } },
  }],
}))

async function loadStats() { stats.value = await api.get('/admin/stats') }
async function loadMessages() { allMessages.value = await api.get('/social/messages?all=true') }
async function loadLinks() { allLinks.value = await api.get('/social/links?all=true') }

async function reviewMsg(m: any, action: string) {
  if (action === 'reply') {
    const reply = prompt('回复内容', m.reply || '')
    if (reply === null) return
    await api.post(`/admin/messages/${m.id}/review`, { action, reply })
  } else {
    await api.post(`/admin/messages/${m.id}/review`, { action })
  }
  toast('操作成功', 'ok')
  loadMessages(); loadStats()
}

async function reviewLink(l: any, status: string) {
  await api.put(`/social/links/${l.id}`, { status })
  toast('已更新', 'ok')
  loadLinks(); loadStats()
}

async function delLink(l: any) {
  if (!confirm(`删除友链「${l.name}」？`)) return
  await api.del(`/social/links/${l.id}`)
  loadLinks()
}

const accents = ['#E4572E', '#3D7A5E', '#D9932C', '#2E86AB', '#D4577A', '#23262B']
async function saveSettings() {
  await api.put('/settings/effects', { value: store.settings.effects })
  await api.put('/settings/theme', { value: store.settings.theme })
  applyAccent()
  toast('配置已生效', 'ok')
}

function switchTab(t: string) {
  tab.value = t
  if (t === 'review') loadMessages()
  if (t === 'links') loadLinks()
}

const statusName: Record<string, string> = { approved: '已展示', pending: '待审核', rejected: '已拦截' }

onMounted(loadStats)
</script>

<template>
  <div>
    <div class="page-head"><h1>后台管理</h1><p>内容、权限、数据，一站式管理控制台</p></div>

    <div class="admin-tabs card">
      <button v-for="t in tabs" :key="t.id" :class="{ on: tab === t.id }" @click="switchTab(t.id)">
        {{ t.name }}
        <i v-if="t.id === 'review' && stats?.pending?.messages" class="badge">{{ stats.pending.messages }}</i>
        <i v-if="t.id === 'links' && stats?.pending?.links" class="badge">{{ stats.pending.links }}</i>
      </button>
    </div>

    <!-- ===== 数据总览 ===== -->
    <template v-if="tab === 'dashboard'">
      <div v-if="stats" class="stat-cards">
        <div class="sc card"><b>{{ stats.totalVisits }}</b><span>总访问量</span></div>
        <div class="sc card"><b>{{ stats.counts.articles }}</b><span>知识库文章</span></div>
        <div class="sc card"><b>{{ stats.counts.moments }}</b><span>生活动态</span></div>
        <div class="sc card"><b>{{ stats.counts.messages }}</b><span>留言总数</span></div>
        <div class="sc card"><b>{{ stats.counts.movies + stats.counts.music }}</b><span>影音收藏</span></div>
        <div class="sc card warn" v-if="stats.pending.messages + stats.pending.links > 0">
          <b>{{ stats.pending.messages + stats.pending.links }}</b><span>待审核项</span>
        </div>
      </div>
      <div class="card chart-card">
        <h3>近 30 天访问趋势</h3>
        <div ref="visitEl" class="chart"></div>
      </div>
    </template>

    <!-- ===== 留言审核 ===== -->
    <template v-else-if="tab === 'review'">
      <div class="card table-card">
        <table>
          <thead><tr><th>留言</th><th>状态</th><th>时间</th><th>互动</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="m in allMessages" :key="m.id">
              <td class="c-msg">
                <strong :style="{ color: m.color }">{{ m.nickname }}</strong>
                <p>{{ m.content }}</p>
                <small v-if="m.reply">回复：{{ m.reply }}</small>
              </td>
              <td><span class="st" :class="m.status">{{ statusName[m.status] }}</span></td>
              <td class="c-time">{{ fromNow(m.created_at) }}</td>
              <td class="c-time">♥ {{ m.likes }}</td>
              <td class="c-ops">
                <button v-if="m.status !== 'approved'" @click="reviewMsg(m, 'approve')">通过</button>
                <button v-if="m.status === 'approved'" @click="reviewMsg(m, 'pin')">{{ m.pinned ? '取消置顶' : '置顶' }}</button>
                <button @click="reviewMsg(m, 'reply')">回复</button>
                <button v-if="m.status === 'pending'" @click="reviewMsg(m, 'reject')">拦截</button>
                <button class="danger" @click="reviewMsg(m, 'delete')">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!allMessages.length" class="empty">暂无留言</div>
      </div>
    </template>

    <!-- ===== 友链管理 ===== -->
    <template v-else-if="tab === 'links'">
      <div class="card table-card">
        <table>
          <thead><tr><th>站点</th><th>链接</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="l in allLinks" :key="l.id">
              <td class="c-msg"><strong>{{ l.name }}</strong><p>{{ l.description }}</p></td>
              <td class="c-time" style="font-family:var(--mono);font-size:12px">{{ l.url.replace(/^https?:\/\//, '').slice(0, 30) }}</td>
              <td><span class="st" :class="l.status">{{ statusName[l.status] }}</span></td>
              <td class="c-ops">
                <button v-if="l.status !== 'approved'" @click="reviewLink(l, 'approved')">通过</button>
                <button v-if="l.status === 'approved'" @click="reviewLink(l, 'rejected')">下架</button>
                <button class="danger" @click="delLink(l)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- ===== 组件与外观 ===== -->
    <template v-else>
      <div class="card settings-card">
        <h3>全局 3D 动态特效</h3>
        <div class="set-row">
          <div><strong>3D 粒子背景</strong><small>关闭后首页 Hero 使用静态渐变背景</small></div>
          <button class="switch" :class="{ on: store.settings.effects.three }"
                  @click="store.settings.effects.three = !store.settings.effects.three"><i></i></button>
        </div>
        <div class="set-row">
          <div><strong>动态强度</strong><small>影响粒子数量与运动幅度（{{ Math.round(store.settings.effects.intensity * 100) }}%）</small></div>
          <input v-model.number="store.settings.effects.intensity" type="range" min="0.2" max="1" step="0.1" class="range" />
        </div>
        <h3 style="margin-top:26px">主题强调色</h3>
        <div class="set-row">
          <div><strong>强调色</strong><small>实时预览，保存后全站生效</small></div>
          <div class="acc-list">
            <i v-for="a in accents" :key="a" :style="{ background: a }"
               :class="{ on: store.settings.theme.accent === a }"
               @click="store.settings.theme.accent = a; applyAccent()"></i>
          </div>
        </div>
        <button class="btn btn-primary" style="margin-top:20px" @click="saveSettings">保存配置</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.admin-tabs { display: flex; gap: 4px; padding: 5px; margin-bottom: 16px; width: fit-content; border-radius: 12px; }
.admin-tabs button {
  padding: 8px 18px; border-radius: 9px; font-size: 13.5px; color: var(--ink-2);
  display: flex; align-items: center; gap: 7px; transition: all .2s;
}
.admin-tabs button.on { background: var(--ink); color: #F5F2EA; font-weight: 500; }
.badge { background: var(--accent); color: #fff; font-size: 11px; font-style: normal; min-width: 17px; height: 17px; border-radius: 99px; display: inline-flex; align-items: center; justify-content: center; padding: 0 4px; }

.stat-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; margin-bottom: 14px; }
.sc { padding: 18px; text-align: center; }
.sc b { font-size: 26px; font-weight: 800; display: block; color: var(--ink); }
.sc span { font-size: 12.5px; color: var(--muted); }
.sc.warn b { color: var(--accent); }
.chart-card { padding: 20px; }
.chart-card h3 { font-size: 15px; margin-bottom: 8px; }
.chart { height: 280px; }

.table-card { padding: 8px 16px; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
th { text-align: left; padding: 12px 10px; color: var(--muted); font-weight: 500; font-size: 12.5px; border-bottom: 1px solid var(--line); }
td { padding: 12px 10px; border-bottom: 1px dashed var(--line-2); vertical-align: top; }
tr:last-child td { border-bottom: none; }
.c-msg { max-width: 320px; }
.c-msg p { color: var(--ink-2); margin: 3px 0; }
.c-msg small { color: var(--green); }
.c-time { color: var(--muted); font-size: 12.5px; white-space: nowrap; }
.c-ops { white-space: nowrap; }
.c-ops button { font-size: 12.5px; color: var(--ink-2); padding: 4px 9px; border-radius: 7px; border: 1px solid var(--line); margin-right: 5px; transition: all .18s; }
.c-ops button:hover { border-color: var(--ink-2); color: var(--ink); }
.c-ops button.danger { color: var(--rose); border-color: #F2D3DE; }
.c-ops button.danger:hover { background: #FCEEF3; }
.st { font-size: 12px; padding: 3px 10px; border-radius: 99px; white-space: nowrap; }
.st.approved { background: var(--green-soft); color: var(--green); }
.st.pending { background: var(--amber-soft); color: var(--amber); }
.st.rejected { background: #F7E3E0; color: var(--accent-strong); }

.settings-card { padding: 24px; max-width: 640px; }
.settings-card h3 { font-size: 16px; margin-bottom: 14px; }
.set-row { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 14px 0; border-bottom: 1px dashed var(--line-2); }
.set-row strong { font-size: 14px; display: block; }
.set-row small { color: var(--muted); font-size: 12.5px; }
.switch { width: 46px; height: 26px; border-radius: 99px; background: #D8D2C4; position: relative; transition: background .25s; flex: none; }
.switch i { position: absolute; top: 3px; left: 3px; width: 20px; height: 20px; border-radius: 50%; background: #fff; transition: transform .25s var(--ease); box-shadow: 0 1px 4px rgba(0,0,0,.2); }
.switch.on { background: var(--green); }
.switch.on i { transform: translateX(20px); }
.range { width: 180px; accent-color: var(--accent); }
.acc-list { display: flex; gap: 10px; }
.acc-list i { width: 30px; height: 30px; border-radius: 10px; cursor: pointer; border: 3px solid transparent; transition: transform .2s; }
.acc-list i.on { border-color: var(--ink); transform: scale(1.1); }
</style>
