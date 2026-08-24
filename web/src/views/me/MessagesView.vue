<script setup lang="ts">
/** 我的 · 留言弹幕墙：全屏弹幕 + 发送 + AI 审核提示（PRD 特色功能） */
import { onMounted, ref } from 'vue'
import { api, fromNow, type Message } from '../../api'
import Danmaku from '../../components/Danmaku.vue'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const list = ref<Message[]>([])
const nickname = ref(localStorage.getItem('opc_nick') || '')
const content = ref('')
const sending = ref(false)
const colors = ['#E4572E', '#3D7A5E', '#E8A13C', '#2E86AB', '#D4577A']
const color = ref(colors[0])

async function load() { list.value = await api.get('/social/messages') }

async function send() {
  if (!content.value.trim()) return toast('写点什么再发射', 'warn')
  sending.value = true
  try {
    const res = await api.post('/social/messages', { nickname: nickname.value || '匿名访客', content: content.value.trim(), color: color.value })
    localStorage.setItem('opc_nick', nickname.value)
    toast(res.tip, res.status === 'approved' ? 'ok' : 'warn')
    content.value = ''
    load()
  } catch (e: any) {
    toast(e.message, 'warn')
  } finally { sending.value = false }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>留言弹幕</h1><p>你的留言会以弹幕形式飞过屏幕 · AI 实时内容审核</p></div>
    <SectionTabs :items="[
      { name: '友情链接', path: '/me/links' }, { name: '留言弹幕', path: '/me/messages' },
      { name: '成长时间轴', path: '/me/timeline' }, { name: '自媒体矩阵', path: '/me/matrix' },
    ]" />

    <!-- 弹幕发射器 -->
    <div class="launcher card">
      <input v-model="nickname" class="input nick" placeholder="昵称" maxlength="12" />
      <input v-model="content" class="input body" placeholder="发射一条弹幕留言…（120 字内）" maxlength="120" @keyup.enter="send" />
      <div class="color-pick">
        <i v-for="c in colors" :key="c" :style="{ background: c }" :class="{ on: color === c }" @click="color = c"></i>
      </div>
      <button class="btn btn-primary" :disabled="sending" @click="send">发射 ♥</button>
    </div>

    <!-- 弹幕墙 -->
    <Danmaku :messages="list" />

    <!-- 留言列表 -->
    <div class="msg-list">
      <h3>全部留言 <em>{{ list.length }}</em></h3>
      <transition-group name="list">
        <div v-for="m in list" :key="m.id" class="msg card">
          <span class="m-dot" :style="{ background: m.color }"></span>
          <div class="m-main">
            <div class="m-head">
              <strong :style="{ color: m.color }">{{ m.nickname }}</strong>
              <span v-if="m.pinned" class="tag hot">置顶</span>
              <small>{{ fromNow(m.created_at) }}</small>
            </div>
            <p>{{ m.content }}</p>
            <div v-if="m.reply" class="m-reply"><b>站长回复：</b>{{ m.reply }}</div>
          </div>
          <button class="m-like" @click="api.post(`/social/messages/${m.id}/like`, {}).then(() => m.likes++)">♥ {{ m.likes || '' }}</button>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<style scoped>
.launcher { display: flex; gap: 10px; padding: 14px; margin-bottom: 14px; align-items: center; flex-wrap: wrap; }
.launcher .nick { width: 110px; flex: none; }
.launcher .body { flex: 1; min-width: 180px; }
.color-pick { display: flex; gap: 6px; }
.color-pick i { width: 22px; height: 22px; border-radius: 50%; cursor: pointer; transition: transform .2s; border: 2.5px solid transparent; }
.color-pick i.on { border-color: var(--ink); transform: scale(1.12); }

.msg-list { margin-top: 20px; }
.msg-list h3 { font-size: 16px; margin-bottom: 12px; }
.msg-list h3 em { font-style: normal; color: var(--muted); font-size: 13px; margin-left: 6px; }
.msg { display: flex; gap: 12px; padding: 14px 18px; margin-bottom: 10px; align-items: flex-start; }
.m-dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 8px; flex: none; }
.m-main { flex: 1; min-width: 0; }
.m-head { display: flex; align-items: center; gap: 10px; }
.m-head strong { font-size: 14px; }
.m-head small { color: var(--muted); font-size: 12px; }
.m-main p { margin: 5px 0; font-size: 14px; color: var(--ink); }
.m-reply { font-size: 12.5px; color: var(--green); background: var(--green-soft); border-radius: 8px; padding: 6px 11px; margin-top: 6px; }
.m-like { color: var(--muted); font-size: 13px; padding: 4px 8px; border-radius: 8px; transition: all .2s; flex: none; }
.m-like:hover { color: var(--rose); background: #FCEEF3; transform: scale(1.08); }
.list-enter-active { transition: all .3s var(--ease); }
.list-enter-from { opacity: 0; transform: translateX(-8px); }
</style>
