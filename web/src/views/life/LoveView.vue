<script setup lang="ts">
/** 生活 · 恋爱记录：在一起天数 + 纪念日时间线 */
import { computed, onMounted, ref } from 'vue'
import { api, isAdmin } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const data = ref<any>({ meta: {}, days: 0, events: [] })
const addOpen = ref(false)
const form = ref({ title: '', event_date: '', description: '', type: 'memory' })

const typeMeta: Record<string, { name: string; cls: string }> = {
  memory: { name: '回忆', cls: 'hot' },
  travel: { name: '旅行', cls: '' },
  anniversary: { name: '纪念日', cls: 'warm' },
}

async function load() { data.value = await api.get('/life/love') }

async function add() {
  if (!form.value.title || !form.value.event_date) return toast('请填写标题和日期', 'warn')
  await api.post('/life/love/events', form.value)
  toast('已记录', 'ok')
  addOpen.value = false
  form.value = { title: '', event_date: '', description: '', type: 'memory' }
  load()
}

async function remove(id: number) {
  if (!confirm('删除这条记录？')) return
  await api.del(`/life/love/events/${id}`)
  load()
}

const anniList = computed(() => {
  const start = data.value.meta?.start_date
  if (!start) return []
  const list: { label: string; date: string; past: boolean }[] = []
  const s = new Date(start)
  const nowD = new Date()
  for (const n of [100, 365, 520, 1000, 1314, 1825]) {
    const t = new Date(s.getTime() + n * 86400000)
    list.push({ label: `在一起 ${n} 天`, date: t.toISOString().slice(0, 10), past: t < nowD })
  }
  return list
})

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>恋爱记录</h1><p>把两个人走过的路，好好收藏</p></div>
    <SectionTabs :items="[
      { name: '朋友圈', path: '/life/moments' }, { name: '恋爱记录', path: '/life/love' },
      { name: '旅拍地图', path: '/life/travel' }, { name: '运动数据', path: '/life/sports' },
      { name: '游戏档案', path: '/life/games' },
    ]" />

    <!-- 天数卡 -->
    <section class="love-hero card">
      <div class="lh-left">
        <div class="names"><b>林一舟</b><span class="heart">♥</span><b>{{ data.meta?.partner }}</b></div>
        <div class="days"><em>{{ data.days }}</em><span>天</span></div>
        <p class="since">自 {{ data.meta?.start_date }} 起，故事还在继续</p>
      </div>
      <div class="lh-story">
        <h4>我们的故事</h4>
        <p>{{ data.meta?.story }}</p>
      </div>
    </section>

    <!-- 纪念日倒数 -->
    <section class="card anni">
      <div class="panel-head"><h3>纪念日</h3></div>
      <div class="anni-grid">
        <div v-for="a in anniList" :key="a.label" class="anni-item" :class="{ past: a.past }">
          <strong>{{ a.label }}</strong>
          <span>{{ a.date }}</span>
          <i>{{ a.past ? '已一起度过' : '敬请期待' }}</i>
        </div>
      </div>
    </section>

    <!-- 事件时间线 -->
    <div class="sec-title">
      <h3>爱的足迹</h3>
      <button v-if="isAdmin()" class="btn btn-primary btn-sm" @click="addOpen = true">+ 记录</button>
    </div>
    <div class="love-line">
      <transition-group name="list">
        <div v-for="e in data.events" :key="e.id" class="ll-item">
          <div class="ll-dot" :class="e.type"></div>
          <div class="ll-card card hoverable">
            <img v-if="e.cover" :src="e.cover" loading="lazy" />
            <div class="ll-body">
              <div class="ll-head">
                <strong>{{ e.title }}</strong>
                <span class="tag" :class="typeMeta[e.type]?.cls">{{ typeMeta[e.type]?.name || '回忆' }}</span>
              </div>
              <p>{{ e.description }}</p>
              <div class="ll-foot">
                <small>{{ e.event_date }}</small>
                <button v-if="isAdmin()" class="rm" @click="remove(e.id)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 新增弹窗 -->
    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>记录一个瞬间</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>标题</label><input v-model="form.title" class="input" /></div>
          <div class="field"><label>日期</label><input v-model="form.event_date" type="date" class="input" /></div>
          <div class="field"><label>类型</label>
            <select v-model="form.type" class="select">
              <option value="memory">回忆</option><option value="travel">旅行</option><option value="anniversary">纪念日</option>
            </select>
          </div>
          <div class="field"><label>描述</label><textarea v-model="form.description" class="textarea" rows="3"></textarea></div>
          <button class="btn btn-primary" style="width:100%" @click="add">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.love-hero {
  display: grid; grid-template-columns: 1fr 1fr; gap: 24px; padding: 32px 36px; margin-bottom: 16px;
  background: linear-gradient(130deg, #FDF3EE, #FBF7EF 60%, #F6F1E5);
  border: 1px solid #F3D9CC;
}
.names { display: flex; align-items: center; gap: 12px; font-size: 18px; }
.names .heart { color: var(--rose); font-size: 22px; animation: beat 1.4s ease-in-out infinite; }
@keyframes beat { 0%,100% { transform: scale(1) } 12% { transform: scale(1.25) } 24% { transform: scale(1) } }
.days em { font-size: 64px; font-weight: 800; font-style: normal; color: var(--rose); line-height: 1.1; letter-spacing: -.02em; }
.days span { font-size: 16px; color: var(--ink-2); margin-left: 8px; }
.since { color: var(--muted); font-size: 13px; margin-top: 6px; }
.lh-story { border-left: 1px dashed #E8C9BB; padding-left: 24px; }
.lh-story h4 { font-size: 14px; color: var(--rose); margin-bottom: 8px; }
.lh-story p { color: var(--ink-2); font-size: 14px; line-height: 1.9; }

.anni { padding: 20px; margin-bottom: 20px; }
.panel-head h3 { font-size: 16px; }
.anni-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
.anni-item { padding: 14px; border-radius: 12px; border: 1px solid var(--line-2); background: var(--surface-2); display: flex; flex-direction: column; gap: 3px; }
.anni-item strong { font-size: 14px; }
.anni-item span { font-size: 12.5px; color: var(--muted); font-family: var(--mono); }
.anni-item i { font-style: normal; font-size: 11.5px; color: var(--amber); }
.anni-item.past { background: var(--green-soft); border-color: transparent; }
.anni-item.past i { color: var(--green); }

.sec-title { display: flex; align-items: center; justify-content: space-between; margin: 6px 0 14px; }
.sec-title h3 { font-size: 17px; }

.love-line { position: relative; padding-left: 26px; max-width: 640px; }
.love-line::before { content: ''; position: absolute; left: 7px; top: 8px; bottom: 8px; width: 2px; background: linear-gradient(var(--rose), var(--amber)); border-radius: 2px; opacity: .4; }
.ll-item { position: relative; margin-bottom: 16px; }
.ll-dot { position: absolute; left: -25px; top: 20px; width: 12px; height: 12px; border-radius: 50%; background: var(--rose); border: 2.5px solid #fff; box-shadow: 0 0 0 2px var(--rose); }
.ll-dot.travel { background: var(--green); box-shadow: 0 0 0 2px var(--green); }
.ll-dot.anniversary { background: var(--amber); box-shadow: 0 0 0 2px var(--amber); }
.ll-card { overflow: hidden; display: flex; }
.ll-card img { width: 180px; object-fit: cover; flex: none; }
.ll-body { padding: 14px 18px; flex: 1; }
.ll-head { display: flex; align-items: center; gap: 10px; }
.ll-body p { color: var(--ink-2); font-size: 13.5px; margin: 6px 0; }
.ll-foot { display: flex; justify-content: space-between; align-items: center; }
.ll-foot small { color: var(--muted); font-family: var(--mono); font-size: 12px; }
.rm { font-size: 12px; color: var(--rose); }
.list-enter-active { transition: all .4s var(--ease); }
.list-enter-from { opacity: 0; transform: translateX(-10px); }

@media (max-width: 860px) {
  .love-hero { grid-template-columns: 1fr; padding: 24px 20px; }
  .lh-story { border-left: none; padding-left: 0; border-top: 1px dashed #E8C9BB; padding-top: 16px; }
  .ll-card img { width: 120px; }
}
</style>
