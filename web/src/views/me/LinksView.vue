<script setup lang="ts">
/** 我的 · 友情链接：展示 + 访客申请 */
import { onMounted, ref } from 'vue'
import { api, type FriendLink } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const list = ref<FriendLink[]>([])
const applyOpen = ref(false)
const form = ref({ name: '', url: '', description: '' })

async function load() { list.value = await api.get('/social/links') }

async function apply() {
  if (!form.value.name || !form.value.url) return toast('名称与链接必填', 'warn')
  const res = await api.post('/social/links', form.value)
  toast(res.status === 'pending' ? '已提交，等待站长审核' : '已添加', 'ok')
  applyOpen.value = false
  form.value = { name: '', url: '', description: '' }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>友情链接</h1><p>互联网是个村落，欢迎串门</p></div>
    <SectionTabs :items="[
      { name: '友情链接', path: '/me/links' }, { name: '留言弹幕', path: '/me/messages' },
      { name: '成长时间轴', path: '/me/timeline' }, { name: '自媒体矩阵', path: '/me/matrix' },
    ]" />

    <div style="margin-bottom:16px">
      <button class="btn btn-dark btn-sm" @click="applyOpen = true">⇄ 申请互换友链</button>
    </div>

    <div class="link-grid">
      <transition-group name="list">
        <a v-for="l in list" :key="l.id" class="link-card card hoverable" :href="l.url" target="_blank" rel="noopener">
          <span class="l-avatar">{{ l.name.slice(0, 1) }}</span>
          <div class="l-main">
            <strong>{{ l.name }}</strong>
            <p>{{ l.description }}</p>
            <small>{{ l.url.replace(/^https?:\/\//, '') }}</small>
          </div>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" class="l-go"><path d="M7 17L17 7M9 7h8v8"/></svg>
        </a>
      </transition-group>
    </div>

    <div v-if="applyOpen" class="modal-mask" @click.self="applyOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>申请友链</h3><button class="icon-btn" @click="applyOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>站点名称</label><input v-model="form.name" class="input" /></div>
          <div class="field"><label>站点链接</label><input v-model="form.url" class="input" placeholder="https://" /></div>
          <div class="field"><label>一句话介绍</label><input v-model="form.description" class="input" /></div>
          <p class="tip">提交后进入站长审核队列，通过后展示在友链列表。</p>
          <button class="btn btn-primary" style="width:100%" @click="apply">提交申请</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.link-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }
.link-card { display: flex; align-items: center; gap: 14px; padding: 18px; }
.l-avatar {
  width: 48px; height: 48px; border-radius: 14px; flex: none;
  background: linear-gradient(135deg, var(--green), #6FA98D); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 700;
}
.link-card:nth-child(3n + 2) .l-avatar { background: linear-gradient(135deg, var(--amber), #E8B96A); }
.link-card:nth-child(3n) .l-avatar { background: linear-gradient(135deg, var(--accent), #F0825D); }
.l-main { flex: 1; min-width: 0; }
.l-main strong { font-size: 15px; }
.l-main p { font-size: 12.5px; color: var(--muted); margin: 3px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.l-main small { font-size: 11.5px; color: var(--green); font-family: var(--mono); }
.l-go { color: var(--muted); transition: all .2s; }
.link-card:hover .l-go { color: var(--accent); transform: translate(2px, -2px); }
.tip { font-size: 12.5px; color: var(--muted); margin-bottom: 14px; }
.list-enter-active { transition: all .35s var(--ease); }
.list-enter-from { opacity: 0; transform: translateY(10px); }
</style>
