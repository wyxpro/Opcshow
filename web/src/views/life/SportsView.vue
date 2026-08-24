<script setup lang="ts">
/** 生活 · 运动数据：ECharts 趋势图 + 类型统计 + 记录录入 */
import { computed, onMounted, ref } from 'vue'
import { api, isAdmin } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { useChart } from '../../components/useChart'
import { toast } from '../../store'

const list = ref<any[]>([])
const stats = ref<Record<string, { count: number; total: number }>>({})
const addOpen = ref(false)
const form = ref({ type: '跑步', sport_date: '', value: 5, duration: 30 })
const chartEl = ref<HTMLElement | null>(null)
const pieEl = ref<HTMLElement | null>(null)

const typeColor: Record<string, string> = { 跑步: '#E4572E', 骑行: '#3D7A5E', 游泳: '#2E86AB', 徒步: '#D9932C' }

async function load() {
  const res = await api.get('/life/sports')
  list.value = res.list
  stats.value = res.stats
}

/* 近 30 天运动量趋势 */
useChart(chartEl, () => {
  const sorted = [...list.value].sort((a, b) => a.sport_date.localeCompare(b.sport_date))
  return {
    grid: { left: 40, right: 16, top: 30, bottom: 28 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category', data: sorted.map(s => s.sport_date.slice(5)),
      axisLine: { lineStyle: { color: '#E6E1D5' } }, axisLabel: { color: '#8C9099', fontSize: 11 },
    },
    yAxis: {
      type: 'value', name: 'km',
      splitLine: { lineStyle: { color: '#F0EBE0' } }, axisLabel: { color: '#8C9099', fontSize: 11 },
    },
    series: [{
      type: 'bar', data: sorted.map(s => ({ value: s.value, itemStyle: { color: typeColor[s.type] || '#E4572E', borderRadius: [5, 5, 0, 0] } })),
      barWidth: '52%',
    }],
    animationDuration: 800,
  }
})

/* 类型占比 */
useChart(pieEl, () => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, textStyle: { color: '#8C9099', fontSize: 12 }, itemWidth: 14 },
  series: [{
    type: 'pie', radius: ['48%', '72%'], center: ['50%', '44%'],
    itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
    label: { show: false },
    data: Object.entries(stats.value).map(([name, s]) => ({
      name, value: +s.total.toFixed(1), itemStyle: { color: typeColor[name] || '#C9BFA9' },
    })),
  }],
}))

const totalKm = computed(() => Object.values(stats.value).reduce((s, v) => s + v.total, 0).toFixed(1))
const totalCount = computed(() => Object.values(stats.value).reduce((s, v) => s + v.count, 0))

async function add() {
  if (!form.value.sport_date) return toast('请选择日期', 'warn')
  await api.post('/life/sports', form.value)
  toast('已记录', 'ok')
  addOpen.value = false
  load()
}

async function remove(id: number) {
  if (!confirm('删除这条记录？')) return
  await api.del(`/life/sports/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>运动数据</h1><p>汗水不会说谎，每一步都算数</p></div>
    <SectionTabs :items="[
      { name: '朋友圈', path: '/life/moments' }, { name: '恋爱记录', path: '/life/love' },
      { name: '旅拍地图', path: '/life/travel' }, { name: '运动数据', path: '/life/sports' },
      { name: '游戏档案', path: '/life/games' },
    ]" />

    <div class="sport-stats">
      <div class="s-card card"><b>{{ totalKm }}</b><span>总里程 km</span></div>
      <div class="s-card card"><b>{{ totalCount }}</b><span>运动次数</span></div>
      <div class="s-card card"><b>{{ stats['跑步']?.count || 0 }}</b><span>跑步次数</span></div>
      <div class="s-card card accent">
        <b>{{ list.length ? (Object.values(stats).reduce((s, v) => s + v.total, 0) / Math.max(totalCount, 1)).toFixed(1) : 0 }}</b>
        <span>平均单次 km</span>
        <button v-if="isAdmin()" class="btn btn-sm" style="background:#fff;color:var(--accent-strong);margin-top:8px" @click="addOpen = true">+ 记一笔</button>
      </div>
    </div>

    <div class="charts">
      <div class="card chart-card"><h3>运动量趋势</h3><div ref="chartEl" class="chart"></div></div>
      <div class="card chart-card"><h3>类型分布</h3><div ref="pieEl" class="chart"></div></div>
    </div>

    <div class="card rec-card">
      <h3>最近记录</h3>
      <div class="rec-list">
        <div v-for="s in list.slice(0, 10)" :key="s.id" class="rec">
          <span class="r-type" :style="{ background: (typeColor[s.type] || '#E4572E') + '1A', color: typeColor[s.type] || '#E4572E' }">{{ s.type }}</span>
          <strong>{{ s.value }} {{ s.unit }}</strong>
          <span class="r-dur">{{ s.duration }} 分钟</span>
          <time>{{ s.sport_date }}</time>
          <button v-if="isAdmin()" class="rm" @click="remove(s.id)">删除</button>
        </div>
      </div>
    </div>

    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>记录运动</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>类型</label>
            <select v-model="form.type" class="select">
              <option>跑步</option><option>骑行</option><option>游泳</option><option>徒步</option>
            </select>
          </div>
          <div class="field"><label>日期</label><input v-model="form.sport_date" type="date" class="input" /></div>
          <div class="field"><label>里程 (km)</label><input v-model.number="form.value" type="number" step="0.1" class="input" /></div>
          <div class="field"><label>时长 (分钟)</label><input v-model.number="form.duration" type="number" class="input" /></div>
          <button class="btn btn-primary" style="width:100%" @click="add">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sport-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 16px; }
.s-card { padding: 20px; text-align: center; }
.s-card b { font-size: 28px; font-weight: 800; color: var(--ink); display: block; }
.s-card span { font-size: 12.5px; color: var(--muted); }
.s-card.accent { background: linear-gradient(135deg, var(--accent), #F07850); border: none; }
.s-card.accent b, .s-card.accent span { color: #FFF6EF; }

.charts { display: grid; grid-template-columns: 1.6fr 1fr; gap: 14px; margin-bottom: 16px; }
.chart-card { padding: 18px; }
.chart-card h3, .rec-card h3 { font-size: 15px; margin-bottom: 8px; }
.chart { height: 260px; }

.rec-card { padding: 18px; }
.rec-list { display: flex; flex-direction: column; }
.rec { display: flex; align-items: center; gap: 14px; padding: 10px 4px; border-bottom: 1px dashed var(--line-2); font-size: 14px; }
.rec:last-child { border-bottom: none; }
.r-type { padding: 3px 11px; border-radius: 999px; font-size: 12px; font-weight: 600; }
.r-dur { color: var(--muted); font-size: 13px; }
.rec time { margin-left: auto; color: var(--muted); font-size: 12.5px; font-family: var(--mono); }
.rm { font-size: 12px; color: var(--rose); }

@media (max-width: 960px) { .charts { grid-template-columns: 1fr; } }
@media (max-width: 860px) { .sport-stats { grid-template-columns: repeat(2, 1fr); } }
</style>
