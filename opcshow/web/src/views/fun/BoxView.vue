<script setup lang="ts">
/** 娱乐 · 百宝箱：自定义收藏夹 + 检索 */
import { computed, onMounted, ref } from 'vue'
import { api, isAdmin } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const cats = ref<any[]>([])
const keyword = ref('')
const addOpen = ref(false)
const addType = ref<'cat' | 'item'>('item')
const form = ref({ category_id: 0, title: '', url: '', description: '', name: '', icon: '✦' })

const filtered = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return cats.value
  return cats.value
    .map(c => ({ ...c, items: c.items.filter((i: any) => (i.title + i.description).toLowerCase().includes(kw)) }))
    .filter(c => c.items.length)
})

async function load() { cats.value = await api.get('/fun/box') }

function openAdd(type: 'cat' | 'item') {
  addType.value = type
  form.value = { category_id: cats.value[0]?.id || 0, title: '', url: '', description: '', name: '', icon: '✦' }
  addOpen.value = true
}

async function add() {
  if (addType.value === 'cat') {
    if (!form.value.name) return toast('请填写收藏夹名称', 'warn')
    await api.post('/fun/box/categories', { name: form.value.name, icon: form.value.icon })
  } else {
    if (!form.value.title) return toast('请填写标题', 'warn')
    await api.post('/fun/box/items', form.value)
  }
  toast('已添加', 'ok')
  addOpen.value = false
  load()
}

async function removeItem(id: number) {
  if (!confirm('删除该收藏？')) return
  await api.del(`/fun/box/items/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>百宝箱</h1><p>收藏一切值得收藏的东西</p></div>
    <SectionTabs :items="[
      { name: '音乐盒', path: '/fun/music' }, { name: '电影收藏', path: '/fun/movies' },
      { name: '百宝箱', path: '/fun/box' },
    ]" />

    <div class="box-tools card">
      <input v-model="keyword" class="input" placeholder="检索收藏…" />
      <template v-if="isAdmin()">
        <button class="btn btn-ghost btn-sm" @click="openAdd('cat')">+ 收藏夹</button>
        <button class="btn btn-primary btn-sm" @click="openAdd('item')">+ 收藏</button>
      </template>
    </div>

    <div class="box-cats">
      <section v-for="c in filtered" :key="c.id" class="box-cat card">
        <header><span class="c-ic">{{ c.icon }}</span><h3>{{ c.name }}</h3><em>{{ c.items.length }}</em></header>
        <div class="c-items">
          <a v-for="i in c.items" :key="i.id" class="c-item" :href="i.url || undefined" target="_blank" rel="noopener"
             :class="{ plain: !i.url }">
            <div class="ci-main">
              <strong>{{ i.title }}</strong>
              <p v-if="i.description">{{ i.description }}</p>
            </div>
            <svg v-if="i.url" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17L17 7M9 7h8v8"/></svg>
            <button v-if="isAdmin()" class="ci-rm" @click.prevent="removeItem(i.id)">✕</button>
          </a>
        </div>
      </section>
    </div>
    <div v-if="!filtered.length" class="empty">没有匹配的收藏</div>

    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>{{ addType === 'cat' ? '新建收藏夹' : '添加收藏' }}</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <template v-if="addType === 'cat'">
            <div class="field"><label>名称</label><input v-model="form.name" class="input" /></div>
            <div class="field"><label>图标（字符）</label><input v-model="form.icon" class="input" maxlength="2" /></div>
          </template>
          <template v-else>
            <div class="field"><label>所属收藏夹</label>
              <select v-model="form.category_id" class="select">
                <option v-for="c in cats" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="field"><label>标题</label><input v-model="form.title" class="input" /></div>
            <div class="field"><label>链接（可空）</label><input v-model="form.url" class="input" /></div>
            <div class="field"><label>描述</label><textarea v-model="form.description" class="textarea" rows="2"></textarea></div>
          </template>
          <button class="btn btn-primary" style="width:100%" @click="add">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.box-tools { display: flex; gap: 10px; padding: 12px; margin-bottom: 18px; }
.box-tools .input { flex: 1; }
.box-cats { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.box-cat { padding: 18px; }
.box-cat header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.c-ic {
  width: 34px; height: 34px; border-radius: 10px; background: var(--amber-soft); color: var(--amber);
  display: flex; align-items: center; justify-content: center; font-size: 16px;
}
.box-cat h3 { font-size: 15.5px; flex: 1; }
.box-cat em { font-style: normal; font-size: 12px; color: var(--muted); background: var(--surface-2); padding: 2px 9px; border-radius: 99px; }
.c-items { display: flex; flex-direction: column; gap: 8px; }
.c-item {
  display: flex; align-items: center; gap: 8px; padding: 11px 13px; border-radius: 11px;
  border: 1px solid var(--line-2); transition: all .22s var(--ease); color: var(--ink-2);
}
.c-item:hover { border-color: var(--amber); background: var(--amber-soft); transform: translateX(3px); }
.c-item.plain { cursor: default; }
.c-item.plain:hover { border-color: var(--line-2); background: transparent; transform: none; }
.ci-main { flex: 1; min-width: 0; }
.ci-main strong { font-size: 13.5px; color: var(--ink); display: block; }
.ci-main p { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ci-rm { color: var(--muted); font-size: 11px; padding: 3px; }
.ci-rm:hover { color: var(--rose); }
@media (max-width: 860px) { .box-cats { grid-template-columns: 1fr; } }
</style>
