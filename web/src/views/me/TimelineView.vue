<script setup lang="ts">
/** 我的 · 成长时间轴 */
import { onMounted, ref } from 'vue'
import { api, isAdmin, type TimelineItem } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const list = ref<TimelineItem[]>([])
const addOpen = ref(false)
const form = ref({ event_date: '', title: '', description: '', tag: '成长' })

const tagColor: Record<string, string> = { 学业: '#2E86AB', 职业: '#E4572E', 生活: '#D4577A', 运动: '#3D7A5E', 作品: '#D9932C', 成长: '#8C9099' }

async function load() { list.value = await api.get('/social/timeline') }

async function add() {
  if (!form.value.title || !form.value.event_date) return toast('请填写标题与日期', 'warn')
  await api.post('/social/timeline', form.value)
  toast('节点已添加', 'ok')
  addOpen.value = false
  load()
}

async function remove(id: number) {
  if (!confirm('删除该节点？')) return
  await api.del(`/social/timeline/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head"><h1>成长时间轴</h1><p>那些把我塑造成今天的关键时刻</p></div>
    <SectionTabs :items="[
      { name: '友情链接', path: '/me/links' }, { name: '留言弹幕', path: '/me/messages' },
      { name: '成长时间轴', path: '/me/timeline' }, { name: '自媒体矩阵', path: '/me/matrix' },
    ]" />

    <div v-if="isAdmin()" style="margin-bottom:18px">
      <button class="btn btn-primary btn-sm" @click="addOpen = true">+ 添加节点</button>
    </div>

    <div class="tl">
      <transition-group name="list">
        <div v-for="(t, i) in list" :key="t.id" class="tl-item" :class="{ right: i % 2 === 1 }">
          <div class="tl-card card hoverable">
            <div class="tl-head">
              <time>{{ t.event_date }}</time>
              <span class="tl-tag" :style="{ background: (tagColor[t.tag] || '#8C9099') + '1A', color: tagColor[t.tag] || '#8C9099' }">{{ t.tag }}</span>
            </div>
            <h3>{{ t.title }}</h3>
            <p>{{ t.description }}</p>
            <button v-if="isAdmin()" class="rm" @click="remove(t.id)">删除</button>
          </div>
          <span class="tl-node" :style="{ background: tagColor[t.tag] || '#8C9099' }"></span>
        </div>
      </transition-group>
    </div>

    <div v-if="addOpen" class="modal-mask" @click.self="addOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>添加成长节点</h3><button class="icon-btn" @click="addOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>日期</label><input v-model="form.event_date" type="date" class="input" /></div>
          <div class="field"><label>标题</label><input v-model="form.title" class="input" /></div>
          <div class="field"><label>标签</label>
            <select v-model="form.tag" class="select"><option>成长</option><option>学业</option><option>职业</option><option>生活</option><option>运动</option><option>作品</option></select>
          </div>
          <div class="field"><label>描述</label><textarea v-model="form.description" class="textarea" rows="3"></textarea></div>
          <button class="btn btn-primary" style="width:100%" @click="add">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tl { position: relative; max-width: 880px; margin: 0 auto; padding: 10px 0 30px; }
.tl::before {
  content: ''; position: absolute; left: 50%; top: 0; bottom: 0; width: 2px;
  background: linear-gradient(var(--accent), var(--amber), var(--green)); transform: translateX(-50%);
  border-radius: 2px; opacity: .5;
}
.tl-item { position: relative; width: 50%; padding: 0 34px 26px 0; }
.tl-item.right { margin-left: 50%; padding: 0 0 26px 34px; }
.tl-node {
  position: absolute; top: 22px; right: -8px; width: 14px; height: 14px; border-radius: 50%;
  border: 3px solid #fff; box-shadow: 0 0 0 2px currentColor; z-index: 2;
}
.tl-item.right .tl-node { right: auto; left: -8px; }
.tl-card { padding: 18px 20px; }
.tl-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.tl-head time { font-family: var(--mono); font-size: 12.5px; color: var(--muted); }
.tl-tag { font-size: 11.5px; padding: 2px 10px; border-radius: 99px; font-weight: 600; }
.tl-card h3 { font-size: 16px; }
.tl-card p { color: var(--ink-2); font-size: 13.5px; margin-top: 6px; line-height: 1.7; }
.rm { margin-top: 8px; font-size: 12px; color: var(--rose); }
.list-enter-active { transition: all .45s var(--ease); }
.list-enter-from { opacity: 0; transform: translateY(16px); }

@media (max-width: 720px) {
  .tl::before { left: 10px; }
  .tl-item, .tl-item.right { width: 100%; margin-left: 0; padding: 0 0 20px 34px; }
  .tl-node, .tl-item.right .tl-node { left: 3px; right: auto; }
}
</style>
