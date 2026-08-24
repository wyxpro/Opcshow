<script setup lang="ts">
/** 沉浸式文章阅读页：Markdown 渲染 + 阅读进度条 */
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, fmtDate, type KbArticle } from '../../api'

const route = useRoute()
const router = useRouter()
const article = ref<KbArticle | null>(null)
const progress = ref(0)

/** 轻量 Markdown 渲染（标题/代码块/引用/列表/粗体） */
function render(md: string): string {
  const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  const blocks: string[] = []
  const lines = md.split('\n')
  let inCode = false, codeBuf: string[] = [], listBuf: string[] = []
  const flushList = () => {
    if (listBuf.length) { blocks.push(`<ul>${listBuf.map(i => `<li>${i}</li>`).join('')}</ul>`); listBuf = [] }
  }
  for (const raw of lines) {
    const line = raw
    if (line.trim().startsWith('```')) {
      if (inCode) { blocks.push(`<pre><code>${esc(codeBuf.join('\n'))}</code></pre>`); codeBuf = []; inCode = false }
      else { flushList(); inCode = true }
      continue
    }
    if (inCode) { codeBuf.push(line); continue }
    const t = line.trim()
    if (!t) { flushList(); continue }
    if (t.startsWith('### ')) { flushList(); blocks.push(`<h3>${inline(esc(t.slice(4)))}</h3>`) }
    else if (t.startsWith('## ')) { flushList(); blocks.push(`<h2>${inline(esc(t.slice(3)))}</h2>`) }
    else if (t.startsWith('# ')) { flushList(); blocks.push(`<h1>${inline(esc(t.slice(2)))}</h1>`) }
    else if (t.startsWith('> ')) { flushList(); blocks.push(`<blockquote>${inline(esc(t.slice(2)))}</blockquote>`) }
    else if (/^[-\d•]/.test(t) && (t.startsWith('- ') || /^\d+\. /.test(t))) {
      listBuf.push(inline(esc(t.replace(/^- |^\d+\. /, ''))))
    } else { flushList(); blocks.push(`<p>${inline(esc(t))}</p>`) }
  }
  flushList()
  return blocks.join('')
}
function inline(s: string): string {
  return s
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}

const html = computed(() => article.value ? render(article.value.content) : '')

function onScroll() {
  const el = document.documentElement
  const max = el.scrollHeight - el.clientHeight
  progress.value = max > 0 ? Math.min(1, el.scrollTop / max) : 0
}

onMounted(async () => {
  article.value = await api.get(`/knowledge/articles/${route.params.id}`)
  window.addEventListener('scroll', onScroll, { passive: true })
})
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <div class="reader">
    <div class="read-progress"><i :style="{ transform: `scaleX(${progress})` }"></i></div>
    <button class="back btn btn-ghost btn-sm" @click="router.push('/work/knowledge')">← 返回知识库</button>

    <article v-if="article" class="paper card">
      <header class="paper-head">
        <h1>{{ article.title }}</h1>
        <div class="meta">
          <span v-for="t in article.tags" :key="t" class="tag">{{ t }}</span>
          <span>{{ fmtDate(article.created_at) }}</span>
          <span>♦ {{ article.views }} 阅读</span>
        </div>
      </header>
      <div class="content" v-html="html"></div>
    </article>
    <div v-else class="skeleton" style="height:400px"></div>
  </div>
</template>

<style scoped>
.reader { max-width: 780px; margin: 0 auto; }
.read-progress { position: fixed; top: 0; left: 0; right: 0; height: 3px; z-index: 120; background: transparent; }
.read-progress i { display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--amber)); transform-origin: left; transition: transform .1s linear; }
.back { margin-bottom: 14px; }
.paper { padding: 44px 52px; }
.paper-head { border-bottom: 1px solid var(--line-2); padding-bottom: 20px; margin-bottom: 26px; }
.paper-head h1 { font-size: 27px; font-weight: 700; line-height: 1.4; }
.meta { display: flex; align-items: center; gap: 12px; margin-top: 12px; font-size: 13px; color: var(--muted); flex-wrap: wrap; }

.content :deep(h1) { font-size: 22px; margin: 26px 0 12px; }
.content :deep(h2) { font-size: 19px; margin: 24px 0 10px; padding-left: 10px; border-left: 3px solid var(--accent); }
.content :deep(h3) { font-size: 16px; margin: 18px 0 8px; }
.content :deep(p) { margin: 12px 0; color: var(--ink-2); line-height: 1.9; }
.content :deep(ul) { margin: 12px 0 12px 22px; color: var(--ink-2); line-height: 1.9; }
.content :deep(blockquote) {
  margin: 14px 0; padding: 12px 18px; border-left: 3px solid var(--amber);
  background: var(--amber-soft); border-radius: 0 10px 10px 0; color: var(--ink-2); font-size: 14px;
}
.content :deep(pre) {
  background: #23262B; color: #EDE9DC; padding: 16px 18px; border-radius: 12px;
  overflow-x: auto; margin: 14px 0; font-family: var(--mono); font-size: 13px; line-height: 1.7;
}
.content :deep(code) { font-family: var(--mono); }
.content :deep(p code), .content :deep(li code) {
  background: var(--bg-deep); padding: 2px 7px; border-radius: 6px; font-size: 13px; color: var(--accent-strong);
}
.content :deep(strong) { color: var(--ink); }

@media (max-width: 860px) { .paper { padding: 26px 20px; } .paper-head h1 { font-size: 22px; } }
</style>
