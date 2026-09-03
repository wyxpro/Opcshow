<script setup lang="ts">
/** 全局悬浮 AI 助手：创作 / 润色 / 答疑 / 简历优化 / 代码辅助 (支持 SSE 流式打字机 + Markdown 渲染) */
import { nextTick, ref } from 'vue'
import { marked } from 'marked'
import { api } from '../api'
import { store } from '../store'

interface Msg { role: 'user' | 'ai'; text: string; mode?: string }

const open = ref(false)
const mode = ref('chat')
const input = ref('')
const loading = ref(false)
const listRef = ref<HTMLElement | null>(null)
const msgs = ref<Msg[]>([])

const modes = [
  { id: 'chat', name: '对话' },
  { id: 'create', name: '创作' },
  { id: 'polish', name: '润色' },
  { id: 'qa', name: '答疑' },
  { id: 'resume', name: '简历' },
  { id: 'code', name: '代码' },
]

function renderMd(content: string): string {
  if (!content) return ''
  try {
    return marked.parse(content) as string
  } catch {
    return content
  }
}

function toggle() {
  open.value = !open.value
  if (open.value && msgs.value.length === 0) {
    msgs.value.push({
      role: 'ai',
      text: store.settings.ai?.welcome || '你好，我是小舟助手。我支持 SSE 流式对话、文案创作、知识库答疑与简历优化。',
    })
  }
}

async function scrollBottom() {
  await nextTick()
  listRef.value?.scrollTo({ top: listRef.value.scrollHeight, behavior: 'smooth' })
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  msgs.value.push({ role: 'user', text, mode: mode.value })
  input.value = ''
  loading.value = true

  // 创建一条空白 AI 消息，准备追加流数据
  const aiMsgIndex = msgs.value.length
  msgs.value.push({ role: 'ai', text: '' })
  scrollBottom()

  await api.stream(
    '/ai/stream',
    { message: text, mode: mode.value },
    (chunkText: string) => {
      // 收到 chunk 时推流更新消息内容并自动滚动
      msgs.value[aiMsgIndex].text += chunkText
      scrollBottom()
    },
    (err: Error) => {
      if (!msgs.value[aiMsgIndex].text) {
        msgs.value[aiMsgIndex].text = `服务响应异常：${err.message}`
      }
      loading.value = false
      scrollBottom()
    },
    () => {
      loading.value = false
      scrollBottom()
    }
  )
}

function quick(prompt: string) {
  input.value = prompt
  send()
}

function copy(text: string) {
  navigator.clipboard?.writeText(text).catch(() => {})
}
</script>

<template>
  <!-- 悬浮球 -->
  <button class="ai-fab" :class="{ active: open }" @click="toggle" aria-label="AI 助手">
    <svg v-if="!open" viewBox="0 0 24 24">
      <path d="M12 3l1.9 4.6L18.5 9l-4.6 1.9L12 15.5l-1.9-4.6L5.5 9l4.6-1.4L12 3z" fill="currentColor" stroke="none"/>
      <path d="M18.5 15l.9 2.1 2.1.9-2.1.9-.9 2.1-.9-2.1-2.1-.9 2.1-.9.9-2.1z" fill="currentColor" stroke="none" opacity=".75"/>
    </svg>
    <svg v-else viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" /></svg>
    <span v-if="!open" class="fab-tip">AI 助手</span>
  </button>

  <!-- 面板 -->
  <transition name="ai-panel">
    <section v-if="open" class="ai-panel card">
      <header class="ai-head">
        <div class="ai-title">
          <span class="ai-dot"></span>
          <strong>小舟助手</strong>
          <small>AI SSE 流式 · 随时待命</small>
        </div>
        <button class="icon-btn" @click="open = false">
          <svg viewBox="0 0 24 24" width="16" height="16"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
        </button>
      </header>

      <div class="ai-modes">
        <button v-for="m in modes" :key="m.id" class="chip" :class="{ on: mode === m.id }" @click="mode = m.id">
          {{ m.name }}
        </button>
      </div>

      <div ref="listRef" class="ai-list">
        <div v-for="(m, i) in msgs" :key="i" class="ai-msg" :class="m.role">
          <!-- AI 消息采用 Markdown 解析渲染，用户消息渲染纯文本 -->
          <div v-if="m.role === 'ai'" class="bubble md-content" @dblclick="copy(m.text)" v-html="renderMd(m.text)"></div>
          <div v-else class="bubble" @dblclick="copy(m.text)">{{ m.text }}</div>
        </div>
        <div v-if="loading && (!msgs.length || !msgs[msgs.length - 1].text)" class="ai-msg ai">
          <div class="bubble typing"><i></i><i></i><i></i></div>
        </div>
      </div>

      <div v-if="msgs.length <= 1" class="ai-quicks">
        <button class="quick" @click="mode = 'create'; quick('帮我写一段个人简介，风格温暖真诚')">写个人简介</button>
        <button class="quick" @click="mode = 'resume'; quick('负责公司官网前端开发，做了很多优化，效果很好')">优化简历描述</button>
        <button class="quick" @click="mode = 'qa'; quick('Vue3 组合式函数怎么设计？')">知识库答疑</button>
      </div>

      <footer class="ai-input">
        <input v-model="input" class="input" placeholder="输入需求，Enter 发送…" @keyup.enter="send" />
        <button class="send" :disabled="loading" @click="send">
          <svg viewBox="0 0 24 24"><path d="M4 12l16-7-5 7 5 7-16-7zM9 12h6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>
        </button>
      </footer>
    </section>
  </transition>
</template>

<style scoped>
.ai-fab {
  position: fixed; right: 26px; bottom: 26px; z-index: 150;
  width: 54px; height: 54px; border-radius: 18px;
  background: var(--ink); color: #F5EFE3;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10px 26px -8px rgba(35, 38, 43, .45);
  transition: all .3s var(--ease-spring);
}
.ai-fab:hover { transform: translateY(-3px) rotate(-4deg); background: var(--accent); }
.ai-fab.active { background: var(--accent); border-radius: 50%; }
.ai-fab svg { width: 26px; height: 26px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; }
.fab-tip {
  position: absolute; right: 62px; top: 50%; transform: translateY(-50%);
  background: var(--ink); color: #F5EFE3; font-size: 12px; padding: 4px 12px;
  border-radius: 999px; white-space: nowrap; opacity: 0; pointer-events: none; transition: opacity .2s;
}
.ai-fab:hover .fab-tip { opacity: 1; }

.ai-panel {
  position: fixed; right: 26px; bottom: 94px; z-index: 150;
  width: 420px; max-width: calc(100vw - 32px); height: 580px; max-height: 75vh;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: var(--shadow-lg); border-radius: 20px;
}
.ai-panel-enter-active { transition: all .35s var(--ease-spring); }
.ai-panel-leave-active { transition: all .2s ease; }
.ai-panel-enter-from, .ai-panel-leave-to { opacity: 0; transform: translateY(20px) scale(.96); }

.ai-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-bottom: 1px solid var(--line-2);
  background: linear-gradient(120deg, var(--surface-2), var(--surface));
}
.ai-title { display: flex; align-items: center; gap: 9px; }
.ai-title strong { font-size: 15px; }
.ai-title small { color: var(--muted); font-size: 12px; }
.ai-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 4px var(--green-soft); }

.ai-modes { display: flex; gap: 6px; padding: 10px 14px; border-bottom: 1px solid var(--line-2); overflow-x: auto; }
.ai-modes .chip { cursor: pointer; flex: none; }

.ai-list { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.ai-msg { display: flex; }
.ai-msg.user { justify-content: flex-end; }
.bubble {
  max-width: 88%; padding: 9px 13px; border-radius: 14px; font-size: 13.5px; line-height: 1.65;
  white-space: pre-wrap; word-break: break-word;
  background: var(--surface-2); border: 1px solid var(--line-2); color: var(--ink);
  border-bottom-left-radius: 4px;
}
.ai-msg.user .bubble {
  background: var(--accent); border-color: transparent; color: #FFF6EF;
  border-radius: 14px; border-bottom-right-radius: 4px;
}

/* Markdown 内联样式与代码块排版 */
.bubble.md-content { white-space: normal; }
.bubble.md-content :deep(p) { margin: 0 0 8px 0; }
.bubble.md-content :deep(p:last-child) { margin-bottom: 0; }
.bubble.md-content :deep(ul), .bubble.md-content :deep(ol) { margin: 4px 0 8px 18px; padding: 0; }
.bubble.md-content :deep(li) { margin-bottom: 3px; }
.bubble.md-content :deep(code) {
  background: rgba(0, 0, 0, 0.06); padding: 2px 5px; border-radius: 4px; font-family: monospace; font-size: 12.5px;
}
.bubble.md-content :deep(pre) {
  background: #1e1e2e; color: #f8f8f2; padding: 10px; border-radius: 8px; overflow-x: auto; margin: 8px 0;
}
.bubble.md-content :deep(pre code) { background: transparent; padding: 0; color: inherit; }

.bubble.typing { display: flex; gap: 5px; padding: 13px 16px; }
.bubble.typing i { width: 6px; height: 6px; border-radius: 50%; background: var(--muted); animation: bounce 1s infinite; }
.bubble.typing i:nth-child(2) { animation-delay: .15s }
.bubble.typing i:nth-child(3) { animation-delay: .3s }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0) } 30% { transform: translateY(-5px) } }

.ai-quicks { display: flex; flex-wrap: wrap; gap: 6px; padding: 0 14px 10px; }
.quick {
  font-size: 12px; padding: 5px 11px; border-radius: 999px;
  border: 1px dashed var(--line); color: var(--ink-2); transition: all .2s;
}
.quick:hover { border-color: var(--accent); color: var(--accent); border-style: solid; }

.ai-input { display: flex; gap: 8px; padding: 10px 14px; border-top: 1px solid var(--line-2); }
.ai-input .input { border-radius: 999px; }
.send {
  width: 40px; height: 40px; border-radius: 50%; flex: none;
  background: var(--accent); color: #FFF6EF; display: flex; align-items: center; justify-content: center;
  transition: all .2s;
}
.send:hover { background: var(--accent-strong); transform: scale(1.06); }
.send svg { width: 19px; height: 19px; }

@media (max-width: 860px) {
  .ai-fab { right: 16px; bottom: calc(74px + env(safe-area-inset-bottom)); width: 48px; height: 48px; }
  .ai-panel { right: 8px; left: 8px; bottom: calc(130px + env(safe-area-inset-bottom)); width: auto; height: 62vh; }
}
</style>
