<script setup lang="ts">
/** 沉浸式文章阅读页：Markdown 渲染 + TOC 目录导航 + 阅读进度条 + 阅读时长估算 */
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { api, fmtDate, type KbArticle } from '../../api'

interface TocItem { id: string; text: string; level: number }

const route = useRoute()
const router = useRouter()
const article = ref<KbArticle | null>(null)
const progress = ref(0)
const toc = ref<TocItem[]>([])

/** 计算字数与预计阅读分钟数 */
const wordCount = computed(() => {
  if (!article.value?.content) return 0
  return article.value.content.replace(/\s+/g, '').length
})

const readTimeMin = computed(() => {
  return Math.max(1, Math.ceil(wordCount.value / 350))
})

/** Markdown 解析并提取目录层级锚点 */
const html = computed(() => {
  if (!article.value?.content) return ''
  const md = article.value.content
  const items: TocItem[] = []
  let headingCount = 0

  // 匹配 # / ## / ### 标题并添加 id
  const customRenderer = {
    heading(text: string, level: number) {
      headingCount++
      const id = `toc-heading-${headingCount}`
      // 提取纯文本做目录展示
      const cleanText = text.replace(/<[^>]+>/g, '')
      items.push({ id, text: cleanText, level })
      return `<h${level} id="${id}">${text}</h${level}>`
    }
  }

  marked.use({ renderer: customRenderer as any })
  const parsedHtml = marked.parse(md) as string
  toc.value = items
  return parsedHtml
})

function scrollTo(id: string) {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

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
  <div class="reader-layout">
    <div class="read-progress"><i :style="{ transform: `scaleX(${progress})` }"></i></div>

    <div class="reader-main">
      <button class="back btn btn-ghost btn-sm" @click="router.push('/work/knowledge')">← 返回知识库</button>

      <article v-if="article" class="paper card">
        <header class="paper-head">
          <h1>{{ article.title }}</h1>
          <div class="meta">
            <span v-for="t in article.tags" :key="t" class="tag">{{ t }}</span>
            <span>{{ fmtDate(article.created_at) }}</span>
            <span>♦ {{ article.views }} 阅读</span>
            <span>✎ {{ wordCount }} 字</span>
            <span>⏱ 约 {{ readTimeMin }} 分钟读完</span>
          </div>
        </header>

        <div class="content md-rendered" v-html="html"></div>
      </article>
      <div v-else class="skeleton" style="height:400px"></div>
    </div>

    <!-- 右侧 TOC 侧边栏目录 -->
    <aside v-if="toc.length > 0" class="toc-aside card">
      <div class="toc-title">目录导航</div>
      <nav class="toc-list">
        <button
          v-for="item in toc"
          :key="item.id"
          class="toc-item"
          :class="`level-${item.level}`"
          @click="scrollTo(item.id)"
        >
          {{ item.text }}
        </button>
      </nav>
    </aside>
  </div>
</template>

<style scoped>
.reader-layout {
  max-width: 1080px; margin: 0 auto;
  display: grid; grid-template-columns: 1fr 240px; gap: 24px; position: relative;
}
.reader-main { min-width: 0; }

.read-progress { position: fixed; top: 0; left: 0; right: 0; height: 3px; z-index: 120; background: transparent; }
.read-progress i { display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--amber)); transform-origin: left; transition: transform .1s linear; }
.back { margin-bottom: 14px; }
.paper { padding: 44px 52px; }
.paper-head { border-bottom: 1px solid var(--line-2); padding-bottom: 20px; margin-bottom: 26px; }
.paper-head h1 { font-size: 27px; font-weight: 700; line-height: 1.4; }
.meta { display: flex; align-items: center; gap: 12px; margin-top: 12px; font-size: 13px; color: var(--muted); flex-wrap: wrap; }

.content :deep(h1) { font-size: 22px; margin: 26px 0 12px; scroll-margin-top: 80px; }
.content :deep(h2) { font-size: 19px; margin: 24px 0 10px; padding-left: 10px; border-left: 3px solid var(--accent); scroll-margin-top: 80px; }
.content :deep(h3) { font-size: 16px; margin: 18px 0 8px; scroll-margin-top: 80px; }
.content :deep(p) { margin: 12px 0; color: var(--ink-2); line-height: 1.9; }
.content :deep(ul), .content :deep(ol) { margin: 12px 0 12px 22px; color: var(--ink-2); line-height: 1.9; }
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

.toc-aside {
  position: sticky; top: 84px; height: fit-content; max-height: calc(100vh - 120px);
  padding: 16px; border-radius: 16px; overflow-y: auto;
}
.toc-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
.toc-list { display: flex; flex-direction: column; gap: 4px; }
.toc-item {
  text-align: left; background: none; border: none; font-size: 13px; color: var(--ink-2);
  padding: 5px 8px; border-radius: 6px; cursor: pointer; transition: all .2s;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.toc-item:hover { background: var(--surface-2); color: var(--accent); }
.toc-item.level-2 { padding-left: 12px; }
.toc-item.level-3 { padding-left: 22px; font-size: 12px; opacity: 0.85; }

@media (max-width: 920px) {
  .reader-layout { grid-template-columns: 1fr; }
  .toc-aside { display: none; }
  .paper { padding: 26px 20px; }
  .paper-head h1 { font-size: 22px; }
}
</style>
