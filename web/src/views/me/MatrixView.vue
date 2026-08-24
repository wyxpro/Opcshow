<script setup lang="ts">
/** 我的 · 自媒体矩阵：账号聚合展示 */
import { onMounted, ref } from 'vue'
import { api, isAdmin } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import ShareCard from '../../components/ShareCard.vue'
import { toast } from '../../store'

const list = ref<any[]>([])
const addOpen = ref(false)
const shareOpen = ref(false)
const form = ref({ platform: '', handle: '', url: '', followers: '0', icon: '◈', description: '' })

async function load() { list.value = await api.get('/social/accounts') }

async function add() {
  if (!form.value.platform) return toast('请填写平台名', 'warn')
  await api.post('/social/accounts', form.value)
  toast('账号已绑定', 'ok')
  addOpen.value = false
  load()
}

async function remove(id: number) {
  if (!confirm('解绑该账号？')) return
  await api.del(`/social/accounts/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>自媒体矩阵</h1><p>全网账号，一处聚合</p></div>
    <SectionTabs :items="[
      { name: '友情链接', path: '/me/links' }, { name: '留言弹幕', path: '/me/messages' },
      { name: '成长时间轴', path: '/me/timeline' }, { name: '自媒体矩阵', path: '/me/matrix' },
    ]" />

    <div class="mx-hero card">
      <div>
        <h3>全平台创作者</h3>
        <p>文字、视频、代码、摄影——在不同平台，表达同一个自己。</p>
      </div>
      <div class="mx-ops">
        <button class="btn btn-primary btn-sm" @click="shareOpen = true">分享矩阵卡片</button>
        <button v-if="isAdmin()" class="btn btn-ghost btn-sm" @click="addOpen = true">+ 绑定账号</button>
      </div>
    </div>

    <div class="mx-grid">
      <transition-group name="list">
        <div v-for="a in list" :key="a.id" class="mx-card card hoverable">
          <span class="mx-icon">{{ a.icon }}</span>
          <div class="mx-main">
            <div class="mx-top">
              <strong>{{ a.platform }}</strong>
              <em class="mx-fans">{{ a.followers }} 关注</em>
            </div>
            <p class="mx-handle">@{{ a.handle }}</p>
            <p class="mx-desc">{{ a.description }}</p>
            <div class="mx-foot">
              <a v-if="a.url" :href="a.url" target="_blank" rel="noopener" class="mx-visit">访问主页 →</a>
              <button v-if="isAdmin()" class="rm" @click="remove(a.id)">解绑</button>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <ShareCard v-if="shareOpen" target="matrix" @close="shareOpen = false" />

    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>绑定自媒体账号</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>平台</label><input v-model="form.platform" class="input" placeholder="Bilibili" /></div>
          <div class="field"><label>账号名</label><input v-model="form.handle" class="input" /></div>
          <div class="field"><label>主页链接</label><input v-model="form.url" class="input" /></div>
          <div class="field"><label>粉丝数（如 1.2w）</label><input v-model="form.followers" class="input" /></div>
          <div class="field"><label>简介</label><input v-model="form.description" class="input" /></div>
          <button class="btn btn-primary" style="width:100%" @click="add">绑定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mx-hero {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 24px 28px; margin-bottom: 18px; flex-wrap: wrap;
  background: linear-gradient(120deg, #FBF8F1, #F3EDE0);
}
.mx-hero h3 { font-size: 19px; }
.mx-hero p { color: var(--ink-2); font-size: 13.5px; margin-top: 4px; }
.mx-ops { display: flex; gap: 10px; }

.mx-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }
.mx-card { display: flex; gap: 14px; padding: 20px; }
.mx-icon {
  width: 46px; height: 46px; border-radius: 14px; flex: none;
  background: var(--ink); color: #F5F0E4; display: flex; align-items: center; justify-content: center; font-size: 19px;
}
.mx-card:nth-child(3n + 2) .mx-icon { background: var(--accent); }
.mx-card:nth-child(3n) .mx-icon { background: var(--green); }
.mx-main { flex: 1; min-width: 0; }
.mx-top { display: flex; align-items: center; justify-content: space-between; }
.mx-top strong { font-size: 15.5px; }
.mx-fans { font-style: normal; font-size: 12px; color: var(--accent-strong); background: var(--accent-soft); padding: 2px 10px; border-radius: 99px; font-weight: 600; }
.mx-handle { font-size: 12.5px; color: var(--muted); font-family: var(--mono); margin: 2px 0 6px; }
.mx-desc { font-size: 13px; color: var(--ink-2); }
.mx-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.mx-visit { font-size: 12.5px; color: var(--accent); font-weight: 500; }
.rm { font-size: 12px; color: var(--rose); }
.list-enter-active { transition: all .35s var(--ease); }
.list-enter-from { opacity: 0; transform: translateY(10px); }
</style>
