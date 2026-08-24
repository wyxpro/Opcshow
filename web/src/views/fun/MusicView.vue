<script setup lang="ts">
/** 娱乐 · 音乐盒：在线播放器（播放列表 / 进度 / 切歌 / 喜欢） */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { api, isAdmin, type Music } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const list = ref<Music[]>([])
const current = ref(0)
const playing = ref(false)
const progress = ref(0)
const curTime = ref(0)
const duration = ref(0)
const addOpen = ref(false)
const form = ref({ title: '', artist: '', url: '' })

const audio = new Audio()
audio.addEventListener('timeupdate', () => {
  curTime.value = audio.currentTime
  duration.value = audio.duration || 0
  progress.value = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0
})
audio.addEventListener('ended', () => next())
audio.addEventListener('error', () => { playing.value = false })

const song = computed(() => list.value[current.value])

async function load() {
  list.value = await api.get('/fun/music')
  if (song.value) audio.src = song.value.url
}

function playAt(i: number) {
  current.value = i
  audio.src = list.value[i].url
  audio.play().then(() => playing.value = true).catch(() => toast('音频加载失败', 'warn'))
}
function toggle() {
  if (!song.value) return
  if (playing.value) { audio.pause(); playing.value = false }
  else {
    if (!audio.src) audio.src = song.value.url
    audio.play().then(() => playing.value = true).catch(() => toast('音频加载失败', 'warn'))
  }
}
function next() { if (list.value.length) playAt((current.value + 1) % list.value.length) }
function prev() { if (list.value.length) playAt((current.value - 1 + list.value.length) % list.value.length) }
function seek(e: MouseEvent) {
  const bar = e.currentTarget as HTMLElement
  const ratio = (e.clientX - bar.getBoundingClientRect().left) / bar.clientWidth
  if (audio.duration) audio.currentTime = ratio * audio.duration
}

async function like(m: Music) {
  await api.post(`/fun/music/${m.id}/like`, {})
  m.liked = 1 - m.liked
}

async function remove(id: number) {
  if (!confirm('移除这首歌？')) return
  await api.del(`/fun/music/${id}`)
  load()
}

async function add() {
  if (!form.value.title || !form.value.url) return toast('标题与链接必填', 'warn')
  await api.post('/fun/music', form.value)
  toast('已添加', 'ok')
  addOpen.value = false
  load()
}

function fmt(s: number) {
  if (!s || !isFinite(s)) return '0:00'
  return `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`
}

onMounted(load)
onBeforeUnmount(() => { audio.pause(); audio.src = '' })
</script>

<template>
  <div>
    <div class="page-head"><h1>音乐盒</h1><p>收藏的旋律，随时可以响起</p></div>
    <SectionTabs :items="[
      { name: '音乐盒', path: '/fun/music' }, { name: '电影收藏', path: '/fun/movies' },
      { name: '百宝箱', path: '/fun/box' },
    ]" />

    <div class="music-layout">
      <!-- 播放器 -->
      <div class="player card">
        <div class="disc-wrap">
          <div class="disc" :class="{ spin: playing }">
            <img :src="song?.cover || 'https://picsum.photos/seed/vinyl/300/300'" />
          </div>
          <div class="tonearm" :class="{ on: playing }"></div>
        </div>
        <div class="p-info">
          <h3>{{ song?.title || '暂无歌曲' }}</h3>
          <p>{{ song?.artist }} · {{ song?.album }}</p>
        </div>
        <div class="p-bar" @click="seek">
          <i :style="{ width: progress + '%' }"></i>
        </div>
        <div class="p-time"><span>{{ fmt(curTime) }}</span><span>{{ fmt(duration) }}</span></div>
        <div class="p-ctrl">
          <button @click="prev" aria-label="上一首"><svg viewBox="0 0 24 24"><path d="M6 5v14M20 5l-11 7 11 7V5z"/></svg></button>
          <button class="play-btn" @click="toggle" aria-label="播放/暂停">
            <svg v-if="!playing" viewBox="0 0 24 24"><path d="M8 5l12 7-12 7V5z"/></svg>
            <svg v-else viewBox="0 0 24 24"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>
          </button>
          <button @click="next" aria-label="下一首"><svg viewBox="0 0 24 24"><path d="M18 5v14M4 5l11 7-11 7V5z"/></svg></button>
        </div>
      </div>

      <!-- 播放列表 -->
      <div class="playlist card">
        <div class="pl-head">
          <h3>播放列表</h3>
          <button v-if="isAdmin()" class="btn btn-ghost btn-sm" @click="addOpen = true">+ 添加音乐</button>
        </div>
        <div class="pl-list">
          <div v-for="(m, i) in list" :key="m.id" class="pl-item" :class="{ on: i === current }" @click="playAt(i)">
            <span class="pl-idx">
              <template v-if="i === current && playing"><i class="eq"><b></b><b></b><b></b></i></template>
              <template v-else>{{ i + 1 }}</template>
            </span>
            <img :src="m.cover || `https://picsum.photos/seed/m${m.id}/80/80`" />
            <div class="pl-info"><strong>{{ m.title }}</strong><small>{{ m.artist }}</small></div>
            <button class="like" :class="{ on: m.liked }" @click.stop="like(m)">♥</button>
            <button v-if="isAdmin()" class="rm" @click.stop="remove(m.id)">✕</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>添加音乐</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>歌名</label><input v-model="form.title" class="input" /></div>
          <div class="field"><label>歌手</label><input v-model="form.artist" class="input" /></div>
          <div class="field"><label>音频链接 (mp3)</label><input v-model="form.url" class="input" placeholder="https://…/song.mp3" /></div>
          <button class="btn btn-primary" style="width:100%" @click="add">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.music-layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 16px; align-items: start; }

.player { padding: 30px; text-align: center; background: linear-gradient(160deg, #FBF8F1, #F5F0E4); }
.disc-wrap { position: relative; width: 210px; margin: 0 auto 20px; }
.disc {
  width: 210px; height: 210px; border-radius: 50%; padding: 14px;
  background: repeating-radial-gradient(circle, #1E2126 0 2px, #26292F 2px 4px);
  box-shadow: 0 18px 40px -12px rgba(30, 33, 38, .5);
}
.disc.spin { animation: spin 6s linear infinite; }
.disc img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; border: 4px solid #F5F0E4; }
@keyframes spin { to { transform: rotate(360deg) } }
.tonearm {
  position: absolute; top: -8px; right: -18px; width: 10px; height: 110px;
  background: linear-gradient(#C9BFA9, #8C8574); border-radius: 6px;
  transform-origin: top center; transform: rotate(-28deg); transition: transform .6s var(--ease);
}
.tonearm.on { transform: rotate(4deg); }
.p-info h3 { font-size: 18px; }
.p-info p { color: var(--muted); font-size: 13px; margin-top: 2px; }
.p-bar { height: 6px; border-radius: 6px; background: #E4DECF; margin-top: 18px; cursor: pointer; overflow: hidden; }
.p-bar i { display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--amber)); border-radius: 6px; transition: width .2s linear; }
.p-time { display: flex; justify-content: space-between; font-size: 11.5px; color: var(--muted); font-family: var(--mono); margin-top: 6px; }
.p-ctrl { display: flex; align-items: center; justify-content: center; gap: 22px; margin-top: 16px; }
.p-ctrl button { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all .2s; color: var(--ink-2); }
.p-ctrl button:hover { background: rgba(228, 87, 46, .1); color: var(--accent); }
.p-ctrl svg { width: 22px; height: 22px; fill: currentColor; }
.play-btn { width: 58px !important; height: 58px !important; background: var(--accent) !important; color: #FFF6EF !important; box-shadow: 0 10px 22px -8px rgba(228, 87, 46, .6); }
.play-btn:hover { transform: scale(1.06); background: var(--accent-strong) !important; }

.playlist { padding: 18px; }
.pl-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.pl-head h3 { font-size: 16px; }
.pl-list { display: flex; flex-direction: column; }
.pl-item { display: flex; align-items: center; gap: 12px; padding: 10px; border-radius: 12px; cursor: pointer; transition: background .2s; }
.pl-item:hover { background: var(--surface-2); }
.pl-item.on { background: var(--accent-soft); }
.pl-idx { width: 26px; text-align: center; color: var(--muted); font-size: 13px; font-family: var(--mono); flex: none; }
.eq { display: inline-flex; gap: 2px; align-items: flex-end; height: 13px; }
.eq b { width: 3px; background: var(--accent); animation: eq 1s ease-in-out infinite; }
.eq b:nth-child(1) { height: 8px; } .eq b:nth-child(2) { height: 13px; animation-delay: .2s } .eq b:nth-child(3) { height: 6px; animation-delay: .4s }
@keyframes eq { 0%,100% { transform: scaleY(.4) } 50% { transform: scaleY(1) } }
.pl-item img { width: 42px; height: 42px; border-radius: 9px; object-fit: cover; }
.pl-info { flex: 1; min-width: 0; }
.pl-info strong { font-size: 14px; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pl-info small { color: var(--muted); font-size: 12px; }
.like { color: var(--muted); font-size: 15px; transition: all .2s; padding: 4px; }
.like.on, .like:hover { color: var(--rose); transform: scale(1.15); }
.rm { color: var(--muted); font-size: 12px; padding: 4px; }
.rm:hover { color: var(--rose); }

@media (max-width: 960px) { .music-layout { grid-template-columns: 1fr; } }
</style>
