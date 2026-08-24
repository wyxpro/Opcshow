<script setup lang="ts">
/** 知识库：三级目录树 + 文章列表 + 检索 + 在线编辑（PRD P0） */
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, fromNow, isAdmin, type KbArticle, type KbCategory } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const router = useRouter()
const tree = ref<KbCategory[]>([])
const articles = ref<KbArticle[]>([])
const total = ref(0)
const page = ref(1)
const keyword = ref('')
const activeCat = ref<number | 0>(0)
const loading = ref(true)
const expanded = ref<Record<number, boolean>>({})

// 编辑弹窗
const editorOpen = ref(false)
const editing = ref<Partial<KbArticle>>({})
const flatCats = ref<KbCategory[]>([])

async function loadTree() {
  tree.value = await api.get('/knowledge/categories')
  flat.value = []
  const walk = (cats: KbCategory[], depth: number) => cats.forEach(c => {
    flat.value!.push({ ...c, name: `${'　'.repeat(depth - 1)}${depth > 0 ? '└ ' : ''}${c.name}` })
    if (c.children?.length) walk(c.children, depth + 1)
  })
  walk(tree.value, 0)
  flatCats.value = flat.value
}
const flat = ref<KbCategory[] | null>(null)

async function loadArticles() {
  loading.value = true
  const q = new URLSearchParams({ page: String(page.value), size: '8' })
  if (activeCat.value) q.set('category_id', String(activeCat.value))
  if (keyword.value.trim()) q.set('keyword', keyword.value.trim())
  const res = await api.get(`/knowledge/articles?${q}`)
  articles.value = res.list
  total.value = res.total
  loading.value = false
}

function selectCat(id: number) {
  activeCat.value = id
  page.value = 1
  loadArticles()
}

function search() { page.value = 1; loadArticles() }

function openEditor(a?: KbArticle) {
  editing.value = a ? { ...a, tags: [...a.tags] } : { title: '', summary: '', content: '', category_id: activeCat.value || undefined, tags: [] }
  editorOpen.value = true
}

async function saveArticle() {
  const e = editing.value
  if (!e.title?.trim()) return toast('请填写标题', 'warn')
  if (e.id) await api.put(`/knowledge/articles/${e.id}`, e)
  else await api.post('/knowledge/articles', e)
  toast('已保存', 'ok')
  editorOpen.value = false
  loadArticles(); loadTree()
}

async function removeArticle(a: KbArticle) {
  if (!confirm(`删除文章「${a.title}」？`)) return
  await api.del(`/knowledge/articles/${a.id}`)
  toast('已删除', 'ok')
  loadArticles(); loadTree()
}

async function addCategory(parentId: number) {
  const name = prompt(parentId ? '输入子目录名称' : '输入一级目录名称')
  if (!name?.trim()) return
  try {
    await api.post('/knowledge/categories', { name: name.trim(), parent_id: parentId })
    toast('目录已创建', 'ok')
    loadTree()
  } catch (e: any) { toast(e.message, 'warn') }
}

function open(a: KbArticle) { router.push(`/work/article/${a.id}`) }

onMounted(() => { loadTree(); loadArticles() })
</script>

<template>
  <div>
    <div class="page-head">
      <h1>知识库</h1>
      <p>三级目录结构化沉淀，支持全文检索与在线编辑</p>
    </div>
    <SectionTabs :items="[
      { name: '知识库', path: '/work/knowledge' },
      { name: '在线简历', path: '/work/resume' },
    ]" />

    <div class="kb-layout">
      <!-- 目录树 -->
      <aside class="kb-tree card">
        <div class="tree-head">
          <strong>目录</strong>
          <button v-if="isAdmin()" class="icon-btn" title="新建一级目录" @click="addCategory(0)">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
          </button>
        </div>
        <a class="tree-item lv0" :class="{ on: activeCat === 0 }" @click="selectCat(0)">
          <span class="dot"></span>全部文章<em>{{ total }}</em>
        </a>
        <template v-for="c1 in tree" :key="c1.id">
          <a class="tree-item lv1" :class="{ on: activeCat === c1.id }" @click="selectCat(c1.id)">
            <svg class="tw" :class="{ open: expanded[c1.id] !== false }" @click.stop="expanded[c1.id] = expanded[c1.id] === false" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            {{ c1.name }}<em>{{ c1.article_count || '' }}</em>
            <b v-if="isAdmin()" class="add-sub" @click.stop="addCategory(c1.id)">+</b>
          </a>
          <template v-if="expanded[c1.id] !== false">
            <template v-for="c2 in c1.children" :key="c2.id">
              <a class="tree-item lv2" :class="{ on: activeCat === c2.id }" @click="selectCat(c2.id)">
                <svg class="tw" :class="{ open: expanded[c2.id] !== false }" @click.stop="expanded[c2.id] = expanded[c2.id] === false" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                {{ c2.name }}<em>{{ c2.article_count || '' }}</em>
                <b v-if="isAdmin()" class="add-sub" @click.stop="addCategory(c2.id)">+</b>
              </a>
              <template v-if="expanded[c2.id] !== false">
                <a v-for="c3 in c2.children" :key="c3.id" class="tree-item lv3"
                   :class="{ on: activeCat === c3.id }" @click="selectCat(c3.id)">
                  {{ c3.name }}<em>{{ c3.article_count || '' }}</em>
                </a>
              </template>
            </template>
          </template>
        </template>
      </aside>

      <!-- 文章区 -->
      <div class="kb-main">
        <div class="kb-tools card">
          <input v-model="keyword" class="input search" placeholder="检索标题 / 摘要 / 正文…" @keyup.enter="search" />
          <button class="btn btn-dark btn-sm" @click="search">搜索</button>
          <button v-if="isAdmin()" class="btn btn-primary btn-sm" @click="openEditor()">写文章</button>
        </div>

        <div v-if="loading" class="skeleton" style="height:300px"></div>
        <div v-else-if="!articles.length" class="empty">暂无文章，换个关键词或目录试试</div>
        <transition-group v-else name="list" tag="div" class="art-list">
          <article v-for="a in articles" :key="a.id" class="art-card card hoverable" @click="open(a)">
            <div class="art-body">
              <h3>{{ a.title }}</h3>
              <p>{{ a.summary }}</p>
              <div class="art-meta">
                <span v-for="t in a.tags" :key="t" class="tag">{{ t }}</span>
                <span class="m">♦ {{ a.views }} 阅读</span>
                <span class="m">{{ fromNow(a.updated_at) }}更新</span>
              </div>
            </div>
            <div v-if="isAdmin()" class="art-ops" @click.stop>
              <button class="icon-btn" title="编辑" @click="openEditor(a)">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20h4L19.5 8.5a2.1 2.1 0 0 0-3-3L5 17v3z"/></svg>
              </button>
              <button class="icon-btn danger" title="删除" @click="removeArticle(a)">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/></svg>
              </button>
            </div>
          </article>
        </transition-group>

        <div v-if="total > 8" class="pager">
          <button class="btn btn-ghost btn-sm" :disabled="page <= 1" @click="page--; loadArticles()">上一页</button>
          <span>{{ page }} / {{ Math.ceil(total / 8) }}</span>
          <button class="btn btn-ghost btn-sm" :disabled="page >= Math.ceil(total / 8)" @click="page++; loadArticles()">下一页</button>
        </div>
      </div>
    </div>

    <!-- 编辑器弹窗 -->
    <div v-if="editorOpen" class="modal-mask" @click.self="editorOpen = false">
      <div class="modal" style="max-width:640px">
        <div class="modal-head">
          <h3>{{ editing.id ? '编辑文章' : '写新文章' }}</h3>
          <button class="icon-btn" @click="editorOpen = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="field"><label>标题</label><input v-model="editing.title" class="input" placeholder="文章标题" /></div>
          <div class="field"><label>所属目录</label>
            <select v-model="editing.category_id" class="select">
              <option v-for="c in flatCats" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="field"><label>摘要</label><input v-model="editing.summary" class="input" placeholder="一句话概括" /></div>
          <div class="field"><label>正文（支持 Markdown）</label>
            <textarea v-model="editing.content" class="textarea" rows="10" placeholder="# 标题&#10;正文内容…"></textarea>
          </div>
          <button class="btn btn-primary" style="width:100%" @click="saveArticle">保存文章</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kb-layout { display: grid; grid-template-columns: 250px 1fr; gap: 16px; align-items: start; }

.kb-tree { padding: 14px 10px; position: sticky; top: 24px; max-height: calc(100vh - 60px); overflow-y: auto; }
.tree-head { display: flex; align-items: center; justify-content: space-between; padding: 2px 10px 10px; font-size: 14px; }
.tree-item {
  display: flex; align-items: center; gap: 6px; padding: 7px 10px; border-radius: 9px;
  font-size: 13.5px; color: var(--ink-2); cursor: pointer; transition: all .18s; position: relative;
}
.tree-item:hover { background: var(--surface-2); color: var(--ink); }
.tree-item.on { background: var(--accent-soft); color: var(--accent-strong); font-weight: 600; }
.tree-item em { margin-left: auto; font-style: normal; font-size: 11.5px; color: var(--muted); }
.tree-item .tw { width: 13px; height: 13px; flex: none; transition: transform .2s; color: var(--muted); }
.tree-item .tw.open { transform: rotate(90deg); }
.lv0 { font-weight: 600; color: var(--ink); }
.lv0 .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); }
.lv2 { padding-left: 26px; }
.lv3 { padding-left: 44px; font-size: 13px; }
.add-sub { display: none; font-weight: 400; color: var(--muted); padding: 0 4px; border-radius: 5px; }
.add-sub:hover { color: var(--accent); background: var(--accent-soft); }
.tree-item:hover .add-sub { display: inline; }

.kb-tools { display: flex; gap: 10px; padding: 12px; margin-bottom: 14px; }
.search { flex: 1; }

.art-list { display: flex; flex-direction: column; gap: 10px; }
.art-card { display: flex; padding: 18px 20px; cursor: pointer; }
.art-body { flex: 1; min-width: 0; }
.art-body h3 { font-size: 16px; font-weight: 600; transition: color .2s; }
.art-card:hover h3 { color: var(--accent); }
.art-body p { font-size: 13.5px; color: var(--muted); margin: 6px 0 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.art-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.art-meta .m { font-size: 12px; color: var(--muted); }
.art-ops { display: flex; flex-direction: column; gap: 4px; }
.icon-btn.danger:hover { background: var(--accent-soft); color: var(--accent-strong); }
.list-enter-active { transition: all .35s var(--ease); }
.list-enter-from { opacity: 0; transform: translateY(10px); }

.pager { display: flex; align-items: center; justify-content: center; gap: 14px; margin-top: 18px; font-size: 13px; color: var(--muted); }

@media (max-width: 860px) {
  .kb-layout { grid-template-columns: 1fr; }
  .kb-tree { position: static; max-height: 220px; }
  .kb-tools { flex-wrap: wrap; }
  .search { flex-basis: 100%; }
}
</style>
