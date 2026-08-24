<script setup lang="ts">
/** 生活 · 朋友圈动态：图文流 + 发布 + 点赞 */
import { onMounted, ref } from 'vue'
import { api, fromNow, isAdmin, type Moment } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const list = ref<Moment[]>([])
const publishOpen = ref(false)
const form = ref({ content: '', location: '', mood: '', images: '' })
const viewerImg = ref('')

async function load() { list.value = await api.get('/life/moments') }

async function publish() {
  if (!form.value.content.trim()) return toast('写点什么吧', 'warn')
  await api.post('/life/moments', {
    ...form.value,
    images: form.value.images.split('\n').map(s => s.trim()).filter(Boolean),
  })
  toast('已发布', 'ok')
  publishOpen.value = false
  form.value = { content: '', location: '', mood: '', images: '' }
  load()
}

async function like(m: Moment) {
  await api.post(`/life/moments/${m.id}/like`, {})
  m.likes++
}

async function remove(m: Moment) {
  if (!confirm('删除这条动态？')) return
  await api.del(`/life/moments/${m.id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>朋友圈</h1><p>记录生活的每个瞬间</p></div>
    <SectionTabs :items="[
      { name: '朋友圈', path: '/life/moments' }, { name: '恋爱记录', path: '/life/love' },
      { name: '旅拍地图', path: '/life/travel' }, { name: '运动数据', path: '/life/sports' },
      { name: '游戏档案', path: '/life/games' },
    ]" />

    <div class="moment-feed">
      <div v-if="isAdmin()" class="composer card" @click="publishOpen = true">
        <span class="c-avatar">舟</span>
        <span class="c-tip">分享此刻的想法…</span>
        <span class="c-icons">◉ ◍ ◐</span>
      </div>

      <transition-group name="list">
        <article v-for="m in list" :key="m.id" class="moment card hoverable">
          <header>
            <span class="m-avatar">舟</span>
            <div class="m-who"><strong>林一舟</strong><small>{{ fromNow(m.created_at) }}<template v-if="m.location"> · ⚲ {{ m.location }}</template></small></div>
            <span v-if="m.mood" class="tag warm">{{ m.mood }}</span>
          </header>
          <p class="m-content">{{ m.content }}</p>
          <div v-if="m.images.length" class="m-imgs" :class="`n${Math.min(m.images.length, 3)}`">
            <img v-for="img in m.images" :key="img" :src="img" loading="lazy" @click="viewerImg = img" />
          </div>
          <footer>
            <button class="m-act" @click="like(m)">♥ {{ m.likes || '' }} 赞</button>
            <button v-if="isAdmin()" class="m-act danger" @click="remove(m)">删除</button>
          </footer>
        </article>
      </transition-group>
    </div>

    <!-- 发布弹窗 -->
    <div v-if="publishOpen" class="modal-mask" @click.self="publishOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>发布动态</h3><button class="icon-btn" @click="publishOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><textarea v-model="form.content" class="textarea" rows="4" placeholder="此刻的想法…" autofocus></textarea></div>
          <div class="field"><label>图片链接（每行一条）</label><textarea v-model="form.images" class="textarea" rows="2" placeholder="https://…"></textarea></div>
          <div class="row2">
            <div class="field"><label>位置</label><input v-model="form.location" class="input" placeholder="杭州" /></div>
            <div class="field"><label>心情</label><input v-model="form.mood" class="input" placeholder="惬意" /></div>
          </div>
          <button class="btn btn-primary" style="width:100%" @click="publish">发布</button>
        </div>
      </div>
    </div>

    <!-- 图片查看器 -->
    <div v-if="viewerImg" class="viewer" @click="viewerImg = ''"><img :src="viewerImg" /></div>
  </div>
</template>

<style scoped>
.moment-feed { max-width: 640px; display: flex; flex-direction: column; gap: 14px; }
.composer { display: flex; align-items: center; gap: 12px; padding: 14px 18px; cursor: pointer; transition: all .25s; }
.composer:hover { box-shadow: var(--shadow-lg); }
.composer:hover .c-tip { color: var(--ink-2); }
.c-avatar, .m-avatar {
  width: 38px; height: 38px; border-radius: 50%; flex: none;
  background: linear-gradient(135deg, var(--accent), var(--amber));
  color: #FFF7EE; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 15px;
}
.c-tip { flex: 1; color: var(--muted); font-size: 14px; transition: color .2s; }
.c-icons { color: var(--muted); letter-spacing: 4px; }

.moment { padding: 18px 20px; }
.moment header { display: flex; align-items: center; gap: 12px; }
.m-who { flex: 1; }
.m-who strong { font-size: 14.5px; display: block; }
.m-who small { color: var(--muted); font-size: 12px; }
.m-content { margin: 12px 0; line-height: 1.8; color: var(--ink); white-space: pre-wrap; }
.m-imgs { display: grid; gap: 6px; border-radius: 12px; overflow: hidden; }
.m-imgs.n1 { grid-template-columns: 1fr; max-width: 380px; }
.m-imgs.n2 { grid-template-columns: 1fr 1fr; }
.m-imgs.n3 { grid-template-columns: repeat(3, 1fr); }
.m-imgs img { width: 100%; aspect-ratio: 4/3; object-fit: cover; cursor: zoom-in; transition: transform .3s var(--ease); }
.m-imgs img:hover { transform: scale(1.03); }
.moment footer { display: flex; gap: 16px; margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--line); }
.m-act { font-size: 13px; color: var(--muted); transition: color .2s; }
.m-act:hover { color: var(--rose); }
.m-act.danger:hover { color: var(--accent-strong); }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.list-enter-active { transition: all .4s var(--ease); }
.list-enter-from { opacity: 0; transform: translateY(14px); }

.viewer {
  position: fixed; inset: 0; z-index: 400; background: rgba(20, 18, 15, .88);
  display: flex; align-items: center; justify-content: center; cursor: zoom-out; padding: 30px;
  animation: fadeIn .2s;
}
.viewer img { max-width: 92vw; max-height: 88vh; border-radius: 12px; box-shadow: var(--shadow-lg); }
</style>
