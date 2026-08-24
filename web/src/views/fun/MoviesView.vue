<script setup lang="ts">
/** 娱乐 · 电影收藏：分类筛选 + 海报墙 + 短评 */
import { onMounted, ref } from 'vue'
import { api, isAdmin, type Movie } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const list = ref<Movie[]>([])
const categories = ref<string[]>([])
const activeCat = ref('')
const activeStatus = ref('')
const addOpen = ref(false)
const form = ref({ title: '', category: '剧情', rating: 8.5, year: 2024, director: '', comment: '', status: '已看' })

async function load() {
  const q = new URLSearchParams()
  if (activeCat.value) q.set('category', activeCat.value)
  if (activeStatus.value) q.set('status', activeStatus.value)
  const res = await api.get(`/fun/movies?${q}`)
  list.value = res.list
  categories.value = res.categories
}

function filter(cat: string) { activeCat.value = activeCat.value === cat ? '' : cat; load() }
function filterStatus(s: string) { activeStatus.value = activeStatus.value === s ? '' : s; load() }

async function add() {
  if (!form.value.title) return toast('请填写片名', 'warn')
  await api.post('/fun/movies', form.value)
  toast('已收藏', 'ok')
  addOpen.value = false
  load()
}

async function remove(id: number) {
  if (!confirm('移除这部电影？')) return
  await api.del(`/fun/movies/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>电影收藏</h1><p>光影里的另一种人生</p></div>
    <SectionTabs :items="[
      { name: '音乐盒', path: '/fun/music' }, { name: '电影收藏', path: '/fun/movies' },
      { name: '百宝箱', path: '/fun/box' },
    ]" />

    <div class="filters">
      <div class="f-row">
        <button v-for="c in categories" :key="c" class="chip" :class="{ on: activeCat === c }" @click="filter(c)">{{ c }}</button>
      </div>
      <div class="f-row">
        <button class="chip" :class="{ on: activeStatus === '已看' }" @click="filterStatus('已看')">已看</button>
        <button class="chip" :class="{ on: activeStatus === '想看' }" @click="filterStatus('想看')">想看</button>
        <button v-if="isAdmin()" class="btn btn-primary btn-sm" style="margin-left:auto" @click="addOpen = true">+ 收藏电影</button>
      </div>
    </div>

    <div class="movie-grid">
      <transition-group name="list">
        <div v-for="m in list" :key="m.id" class="movie card hoverable">
          <div class="mv-poster">
            <img :src="m.poster || `https://picsum.photos/seed/film${m.id}/300/420`" loading="lazy" />
            <span class="mv-rating">{{ m.rating.toFixed(1) }}</span>
            <span class="mv-status" :class="{ want: m.status === '想看' }">{{ m.status }}</span>
          </div>
          <div class="mv-body">
            <h3>{{ m.title }} <small>{{ m.year }}</small></h3>
            <p class="mv-dir">{{ m.director }} 导演</p>
            <p v-if="m.comment" class="mv-comment">“{{ m.comment }}”</p>
            <button v-if="isAdmin()" class="rm" @click="remove(m.id)">移除</button>
          </div>
        </div>
      </transition-group>
    </div>
    <div v-if="!list.length" class="empty">该分类下暂无收藏</div>

    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>收藏电影</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>片名</label><input v-model="form.title" class="input" /></div>
          <div class="row2">
            <div class="field"><label>分类</label>
              <select v-model="form.category" class="select"><option>剧情</option><option>科幻</option><option>动画</option><option>纪录片</option><option>悬疑</option></select>
            </div>
            <div class="field"><label>状态</label>
              <select v-model="form.status" class="select"><option>已看</option><option>想看</option></select>
            </div>
          </div>
          <div class="row2">
            <div class="field"><label>评分</label><input v-model.number="form.rating" type="number" step="0.1" min="0" max="10" class="input" /></div>
            <div class="field"><label>年份</label><input v-model.number="form.year" type="number" class="input" /></div>
          </div>
          <div class="field"><label>导演</label><input v-model="form.director" class="input" /></div>
          <div class="field"><label>短评</label><textarea v-model="form.comment" class="textarea" rows="2"></textarea></div>
          <button class="btn btn-primary" style="width:100%" @click="add">收藏</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filters { display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px; }
.f-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.f-row .chip { cursor: pointer; }

.movie-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 16px; }
.movie { overflow: hidden; }
.mv-poster { position: relative; aspect-ratio: 5/7; overflow: hidden; }
.mv-poster img { width: 100%; height: 100%; object-fit: cover; transition: transform .5s var(--ease); }
.movie:hover .mv-poster img { transform: scale(1.05); }
.mv-rating {
  position: absolute; top: 10px; left: 10px; padding: 3px 10px; border-radius: 9px;
  background: rgba(24, 22, 18, .78); color: #F2C94C; font-weight: 700; font-size: 13.5px;
  font-family: var(--mono); backdrop-filter: blur(4px);
}
.mv-status {
  position: absolute; top: 10px; right: 10px; padding: 3px 10px; border-radius: 9px;
  background: rgba(61, 122, 94, .88); color: #fff; font-size: 11.5px; backdrop-filter: blur(4px);
}
.mv-status.want { background: rgba(217, 147, 44, .9); }
.mv-body { padding: 13px 15px 15px; }
.mv-body h3 { font-size: 15px; }
.mv-body h3 small { color: var(--muted); font-weight: 400; font-size: 12px; }
.mv-dir { font-size: 12px; color: var(--muted); margin: 2px 0 8px; }
.mv-comment {
  font-size: 12.5px; color: var(--ink-2); background: var(--surface-2); border-radius: 9px;
  padding: 8px 11px; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.rm { margin-top: 8px; font-size: 12px; color: var(--rose); }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.list-enter-active { transition: all .35s var(--ease); }
.list-enter-from { opacity: 0; transform: translateY(12px); }
</style>
