<script setup lang="ts">
/** 生活 · 旅拍地图：点位可视化 + 点位相册（抽象轨迹图，接入高德仅需替换底图层） */
import { computed, onMounted, ref } from 'vue'
import { api, isAdmin, type TravelPoint } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const points = ref<TravelPoint[]>([])
const active = ref<TravelPoint | null>(null)
const addOpen = ref(false)
const form = ref({ name: '', region: '', visit_date: '', note: '', x: 50, y: 50 })

const totalPhotos = computed(() => points.value.reduce((s, p) => s + p.photos.length, 0))

async function load() {
  points.value = await api.get('/life/travel')
  if (points.value.length && !active.value) active.value = points.value[0]
}

async function add() {
  if (!form.value.name) return toast('请填写地点名称', 'warn')
  await api.post('/life/travel', { ...form.value, photos: [] })
  toast('点位已添加', 'ok')
  addOpen.value = false
  load()
}

async function remove(p: TravelPoint) {
  if (!confirm(`删除点位「${p.name}」？`)) return
  await api.del(`/life/travel/${p.id}`)
  active.value = null
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>旅拍地图</h1><p>照片与地点绑定，点亮走过的地方（接入高德地图 API 仅需替换底图）</p></div>
    <SectionTabs :items="[
      { name: '朋友圈', path: '/life/moments' }, { name: '恋爱记录', path: '/life/love' },
      { name: '旅拍地图', path: '/life/travel' }, { name: '运动数据', path: '/life/sports' },
      { name: '游戏档案', path: '/life/games' },
    ]" />

    <div class="travel-layout">
      <!-- 轨迹图 -->
      <div class="map-card card">
        <div class="map-stats">
          <span><b>{{ points.length }}</b> 个目的地</span>
          <span><b>{{ totalPhotos }}</b> 张照片</span>
          <button v-if="isAdmin()" class="btn btn-primary btn-sm" @click="addOpen = true">+ 添加点位</button>
        </div>
        <svg class="map" viewBox="0 0 100 88" preserveAspectRatio="xMidYMid meet">
          <defs>
            <radialGradient id="pg" cx="50%" cy="50%">
              <stop offset="0%" stop-color="#E4572E" stop-opacity=".35" />
              <stop offset="100%" stop-color="#E4572E" stop-opacity="0" />
            </radialGradient>
          </defs>
          <!-- 点阵底图（抽象地图质感） -->
          <g fill="#DDD6C6">
            <template v-for="i in 25" :key="'col-' + i">
              <circle v-for="j in 22" :key="i * 100 + j"
                      :cx="i * 4" :cy="j * 4" r=".55"
                      :opacity="((i * 13 + j * 7) % 9) > 3 ? .9 : .25" />
            </template>
          </g>
          <!-- 轨迹连线（按时间顺序） -->
          <polyline :points="points.map(p => `${p.x},${p.y}`).join(' ')"
                    fill="none" stroke="#E4572E" stroke-width=".7" stroke-dasharray="2 1.6" stroke-linecap="round" opacity=".7" />
          <!-- 点位 -->
          <g v-for="p in points" :key="p.id" class="pt" :class="{ on: active?.id === p.id }" @click="active = p">
            <circle :cx="p.x" :cy="p.y" r="7" fill="url(#pg)" class="halo" />
            <circle :cx="p.x" :cy="p.y" r="1.9" :fill="active?.id === p.id ? '#E4572E' : '#3D7A5E'" stroke="#fff" stroke-width=".7" />
            <text :x="p.x" :y="p.y - 4" text-anchor="middle">{{ p.name.split(' ')[0] }}</text>
          </g>
        </svg>
        <p class="map-tip">虚线为旅行轨迹 · 点击点位查看相册 · 生产环境可接入高德地图 JS API 替换底图</p>
      </div>

      <!-- 点位详情 -->
      <aside class="tp-detail card" v-if="active">
        <div class="tp-head">
          <div>
            <h3>{{ active.name }}</h3>
            <small>{{ active.region }} · {{ active.visit_date }}</small>
          </div>
          <button v-if="isAdmin()" class="rm" @click="remove(active)">删除</button>
        </div>
        <p class="tp-note">“{{ active.note }}”</p>
        <div class="tp-photos">
          <img v-for="ph in active.photos" :key="ph" :src="ph" loading="lazy" />
          <div v-if="!active.photos.length" class="empty" style="padding:24px">暂无照片</div>
        </div>
      </aside>
    </div>

    <!-- 添加弹窗 -->
    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>添加旅拍点位</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>地点名称</label><input v-model="form.name" class="input" placeholder="大理 · 洱海" /></div>
          <div class="field"><label>区域</label><input v-model="form.region" class="input" placeholder="云南" /></div>
          <div class="field"><label>日期</label><input v-model="form.visit_date" type="date" class="input" /></div>
          <div class="field"><label>备注</label><textarea v-model="form.note" class="textarea" rows="2"></textarea></div>
          <div class="field"><label>坐标（0-100 抽象坐标系，接入高德后为经纬度）</label>
            <div class="xy">
              <input v-model.number="form.x" type="range" min="5" max="95" class="range" />
              <input v-model.number="form.y" type="range" min="5" max="83" class="range" />
            </div>
          </div>
          <button class="btn btn-primary" style="width:100%" @click="add">保存点位</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.travel-layout { display: grid; grid-template-columns: 1.5fr 1fr; gap: 16px; align-items: start; }
.map-card { padding: 18px; }
.map-stats { display: flex; align-items: center; gap: 18px; margin-bottom: 12px; font-size: 13.5px; color: var(--ink-2); }
.map-stats b { color: var(--accent); font-size: 18px; margin-right: 2px; }
.map-stats .btn { margin-left: auto; }
.map { width: 100%; border-radius: 12px; background: linear-gradient(150deg, #FBF9F2, #F3EEE1); border: 1px solid var(--line-2); }
.map .pt { cursor: pointer; }
.map .pt text { font-size: 3.1px; fill: var(--ink-2); font-weight: 600; pointer-events: none; }
.map .pt .halo { animation: halo 2.6s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }
.map .pt.on .halo { animation-duration: 1.2s; }
@keyframes halo { 0%,100% { transform: scale(.7); opacity: .5 } 50% { transform: scale(1.25); opacity: 1 } }
.map-tip { font-size: 12px; color: var(--muted); margin-top: 10px; }

.tp-detail { padding: 20px; position: sticky; top: 24px; }
.tp-head { display: flex; justify-content: space-between; align-items: flex-start; }
.tp-head h3 { font-size: 17px; }
.tp-head small { color: var(--muted); font-size: 12.5px; }
.rm { font-size: 12.5px; color: var(--rose); }
.tp-note { margin: 12px 0; padding: 12px 16px; background: var(--amber-soft); border-radius: 10px; color: var(--ink-2); font-size: 13.5px; }
.tp-photos { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.tp-photos img { border-radius: 10px; aspect-ratio: 4/3; object-fit: cover; transition: transform .3s; }
.tp-photos img:hover { transform: scale(1.04); }
.xy { display: flex; flex-direction: column; gap: 6px; }
.range { accent-color: var(--accent); }

@media (max-width: 960px) { .travel-layout { grid-template-columns: 1fr; } .tp-detail { position: static; } }
</style>
