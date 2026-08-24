<script setup lang="ts">
/** 生活 · 游戏档案：资料卡片墙 */
import { onMounted, ref } from 'vue'
import { api, isAdmin } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const list = ref<any[]>([])
const addOpen = ref(false)
const form = ref({ name: '', platform: 'Switch', role: '', level: '', hours: 0, achievement: '' })

async function load() { list.value = await api.get('/life/games') }

async function add() {
  if (!form.value.name) return toast('请填写游戏名', 'warn')
  await api.post('/life/games', form.value)
  toast('已入库', 'ok')
  addOpen.value = false
  load()
}

async function remove(id: number) {
  if (!confirm('移出档案？')) return
  await api.del(`/life/games/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>游戏档案</h1><p>虚拟世界里的另一段人生</p></div>
    <SectionTabs :items="[
      { name: '朋友圈', path: '/life/moments' }, { name: '恋爱记录', path: '/life/love' },
      { name: '旅拍地图', path: '/life/travel' }, { name: '运动数据', path: '/life/sports' },
      { name: '游戏档案', path: '/life/games' },
    ]" />

    <div v-if="isAdmin()" style="margin-bottom:14px">
      <button class="btn btn-primary btn-sm" @click="addOpen = true">+ 添加游戏</button>
    </div>

    <div class="game-grid">
      <transition-group name="list">
        <div v-for="g in list" :key="g.id" class="game-card card hoverable">
          <div class="g-cover">
            <img :src="g.cover || `https://picsum.photos/seed/game${g.id}/400/240`" loading="lazy" />
            <span class="g-platform">{{ g.platform }}</span>
          </div>
          <div class="g-body">
            <h3>{{ g.name }}</h3>
            <div class="g-meta">
              <span>角色 · {{ g.role || '—' }}</span>
              <span>进度 · {{ g.level || '—' }}</span>
            </div>
            <div class="g-foot">
              <span class="g-hours"><b>{{ g.hours }}</b> 小时</span>
              <button v-if="isAdmin()" class="rm" @click="remove(g.id)">移出</button>
            </div>
            <p v-if="g.achievement" class="g-ach">✦ {{ g.achievement }}</p>
          </div>
        </div>
      </transition-group>
    </div>

    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>添加游戏</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>游戏名</label><input v-model="form.name" class="input" /></div>
          <div class="field"><label>平台</label>
            <select v-model="form.platform" class="select"><option>Switch</option><option>PS5</option><option>PC</option><option>Xbox</option><option>Mobile</option></select>
          </div>
          <div class="field"><label>角色 / 职业</label><input v-model="form.role" class="input" /></div>
          <div class="field"><label>进度 / 等级</label><input v-model="form.level" class="input" /></div>
          <div class="field"><label>游戏时长（小时）</label><input v-model.number="form.hours" type="number" class="input" /></div>
          <div class="field"><label>成就备注</label><input v-model="form.achievement" class="input" /></div>
          <button class="btn btn-primary" style="width:100%" @click="add">入库</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.game-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; }
.game-card { overflow: hidden; }
.g-cover { position: relative; aspect-ratio: 16/9; overflow: hidden; }
.g-cover img { width: 100%; height: 100%; object-fit: cover; transition: transform .5s var(--ease); }
.game-card:hover .g-cover img { transform: scale(1.06); }
.g-platform {
  position: absolute; top: 10px; right: 10px; padding: 3px 11px; border-radius: 999px;
  background: rgba(24, 22, 18, .72); color: #F5F0E4; font-size: 11.5px; backdrop-filter: blur(4px);
}
.g-body { padding: 14px 16px 16px; }
.g-body h3 { font-size: 15.5px; }
.g-meta { display: flex; flex-direction: column; gap: 2px; margin: 8px 0; font-size: 12.5px; color: var(--muted); }
.g-foot { display: flex; justify-content: space-between; align-items: center; }
.g-hours b { color: var(--accent); font-size: 18px; }
.g-hours { font-size: 12.5px; color: var(--muted); }
.g-ach { margin-top: 8px; font-size: 12px; color: var(--amber); background: var(--amber-soft); padding: 5px 10px; border-radius: 8px; }
.rm { font-size: 12px; color: var(--rose); }
.list-enter-active { transition: all .4s var(--ease); }
.list-enter-from { opacity: 0; transform: scale(.95); }
</style>
