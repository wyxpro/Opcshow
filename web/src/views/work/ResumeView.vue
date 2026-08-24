<script setup lang="ts">
/** 在线简历：多模板 + 可视化编辑 + AI 优化 + 打印导出 PDF（PRD P0） */
import { onMounted, ref } from 'vue'
import { api, isAdmin } from '../../api'
import SectionTabs from '../../components/SectionTabs.vue'
import { toast } from '../../store'

const resume = ref<any>(null)
const template = ref('minimal')
const editOpen = ref(false)
const editSection = ref('basic')
const aiOpen = ref(false)
const aiInput = ref('')
const aiResult = ref('')
const aiLoading = ref(false)
const saving = ref(false)

const templates = [
  { id: 'minimal', name: '极简白', desc: '留白克制，内容为王' },
  { id: 'business', name: '商务墨', desc: '深色侧栏，稳重专业' },
  { id: 'creative', name: '创意橙', desc: '色块点缀，彰显个性' },
]

async function load() {
  const r = await api.get('/resume')
  resume.value = r.data
  template.value = r.template || 'minimal'
}

async function save() {
  saving.value = true
  await api.put('/resume', { name: '我的简历', template: template.value, data: resume.value })
  saving.value = false
  toast('简历已保存', 'ok')
}

async function aiOptimize() {
  if (!aiInput.value.trim()) return
  aiLoading.value = true
  aiResult.value = ''
  try {
    const res = await api.post('/ai/chat', { message: aiInput.value, mode: 'resume' })
    aiResult.value = res.reply
  } finally { aiLoading.value = false }
}

function applyAi() {
  if (!aiResult.value) return
  resume.value.summary = aiResult.value.replace(/▸ 原表述：.*\n\n▸ 优化后：/, '').split('\n\n▸ 建议')[0]
  aiOpen.value = false
  toast('已应用到个人总结', 'ok')
}

function exportPdf() {
  toast('在打印对话框中选择「另存为 PDF」', 'ok')
  setTimeout(() => window.print(), 350)
}

function addItem(section: string, item: any) { resume.value[section].push(item) }
function removeItem(section: string, i: number) { resume.value[section].splice(i, 1) }

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head no-print">
      <h1>在线简历</h1>
      <p>选择模板 · 可视化编辑 · AI 优化 · 一键导出 PDF</p>
    </div>
    <div class="no-print">
      <SectionTabs :items="[
        { name: '知识库', path: '/work/knowledge' },
        { name: '在线简历', path: '/work/resume' },
      ]" />
    </div>

    <!-- 工具条 -->
    <div class="toolbar card no-print">
      <div class="tpl-list">
        <div v-for="t in templates" :key="t.id" class="tpl" :class="{ on: template === t.id }" @click="template = t.id">
          <i :class="t.id"></i>
          <div><strong>{{ t.name }}</strong><small>{{ t.desc }}</small></div>
        </div>
      </div>
      <div class="ops">
        <button class="btn btn-ghost btn-sm" @click="aiOpen = true">✦ AI 优化</button>
        <button v-if="isAdmin()" class="btn btn-ghost btn-sm" @click="editOpen = !editOpen">{{ editOpen ? '收起编辑' : '编辑内容' }}</button>
        <button v-if="isAdmin()" class="btn btn-dark btn-sm" :disabled="saving" @click="save">保存</button>
        <button class="btn btn-primary btn-sm" @click="exportPdf">导出 PDF</button>
      </div>
    </div>

    <div class="resume-layout">
      <!-- 编辑面板 -->
      <aside v-if="editOpen && isAdmin() && resume" class="edit-panel card no-print">
        <div class="ep-tabs">
          <button v-for="s in [['basic','基本'],['summary','总结'],['experience','经历'],['education','教育'],['projects','项目'],['skills','技能']]"
                  :key="s[0]" :class="{ on: editSection === s[0] }" @click="editSection = s[0]">{{ s[1] }}</button>
        </div>

        <div v-if="editSection === 'basic'" class="ep-body">
          <div class="field"><label>姓名</label><input v-model="resume.basic.name" class="input" /></div>
          <div class="field"><label>职位</label><input v-model="resume.basic.title" class="input" /></div>
          <div class="field"><label>电话</label><input v-model="resume.basic.phone" class="input" /></div>
          <div class="field"><label>邮箱</label><input v-model="resume.basic.email" class="input" /></div>
          <div class="field"><label>城市</label><input v-model="resume.basic.location" class="input" /></div>
        </div>
        <div v-else-if="editSection === 'summary'" class="ep-body">
          <div class="field"><label>个人总结</label><textarea v-model="resume.summary" class="textarea" rows="6"></textarea></div>
        </div>
        <div v-else-if="editSection === 'experience'" class="ep-body">
          <div v-for="(e, i) in resume.experience" :key="i" class="ep-item">
            <input v-model="e.company" class="input" placeholder="公司" />
            <input v-model="e.role" class="input" placeholder="职位" />
            <input v-model="e.period" class="input" placeholder="时间段" />
            <textarea v-model="e.desc" class="textarea" rows="3" placeholder="工作描述"></textarea>
            <button class="rm" @click="removeItem('experience', i)">删除该段</button>
          </div>
          <button class="btn btn-ghost btn-sm" @click="addItem('experience', { company: '', role: '', period: '', desc: '' })">+ 添加经历</button>
        </div>
        <div v-else-if="editSection === 'education'" class="ep-body">
          <div v-for="(e, i) in resume.education" :key="i" class="ep-item">
            <input v-model="e.school" class="input" placeholder="学校" />
            <input v-model="e.major" class="input" placeholder="专业" />
            <input v-model="e.period" class="input" placeholder="时间段" />
            <button class="rm" @click="removeItem('education', i)">删除</button>
          </div>
          <button class="btn btn-ghost btn-sm" @click="addItem('education', { school: '', major: '', period: '', degree: '' })">+ 添加教育</button>
        </div>
        <div v-else-if="editSection === 'projects'" class="ep-body">
          <div v-for="(p, i) in resume.projects" :key="i" class="ep-item">
            <input v-model="p.name" class="input" placeholder="项目名" />
            <input v-model="p.role" class="input" placeholder="角色" />
            <textarea v-model="p.desc" class="textarea" rows="3" placeholder="项目描述"></textarea>
            <button class="rm" @click="removeItem('projects', i)">删除</button>
          </div>
          <button class="btn btn-ghost btn-sm" @click="addItem('projects', { name: '', role: '', period: '', desc: '' })">+ 添加项目</button>
        </div>
        <div v-else class="ep-body">
          <div class="field"><label>技能（每行一条）</label>
            <textarea :value="resume.skills.join('\n')" class="textarea" rows="7"
                      @change="resume.skills = ($event.target as HTMLTextAreaElement).value.split('\n').filter(Boolean)"></textarea>
          </div>
        </div>
      </aside>

      <!-- 简历预览（打印区域） -->
      <div v-if="resume" class="resume-paper" :class="template">
        <header class="r-head">
          <div>
            <h1>{{ resume.basic.name }}</h1>
            <p class="r-title">{{ resume.basic.title }} · {{ resume.basic.years }}</p>
          </div>
          <div class="r-contact">
            <span>{{ resume.basic.phone }}</span>
            <span>{{ resume.basic.email }}</span>
            <span>{{ resume.basic.location }}</span>
          </div>
        </header>

        <section class="r-sec">
          <h2>个人总结</h2>
          <p>{{ resume.summary }}</p>
        </section>

        <section class="r-sec">
          <h2>工作经历</h2>
          <div v-for="(e, i) in resume.experience" :key="i" class="r-item">
            <div class="r-line"><strong>{{ e.company }} · {{ e.role }}</strong><em>{{ e.period }}</em></div>
            <p>{{ e.desc }}</p>
          </div>
        </section>

        <section class="r-sec">
          <h2>项目经历</h2>
          <div v-for="(p, i) in resume.projects" :key="i" class="r-item">
            <div class="r-line"><strong>{{ p.name }} · {{ p.role }}</strong><em>{{ p.period }}</em></div>
            <p>{{ p.desc }}</p>
          </div>
        </section>

        <section class="r-sec">
          <h2>教育背景</h2>
          <div v-for="(e, i) in resume.education" :key="i" class="r-item">
            <div class="r-line"><strong>{{ e.school }} · {{ e.major }}（{{ e.degree }}）</strong><em>{{ e.period }}</em></div>
          </div>
        </section>

        <section class="r-sec">
          <h2>专业技能</h2>
          <div class="r-skills"><span v-for="s in resume.skills" :key="s">{{ s }}</span></div>
        </section>
      </div>
    </div>

    <!-- AI 优化弹窗 -->
    <div v-if="aiOpen" class="modal-mask no-print" @click.self="aiOpen = false">
      <div class="modal">
        <div class="modal-head"><h3>✦ AI 简历优化</h3><button class="icon-btn" @click="aiOpen = false">✕</button></div>
        <div class="modal-body">
          <div class="field"><label>粘贴一段简历描述，AI 按 STAR 法则优化</label>
            <textarea v-model="aiInput" class="textarea" rows="4" placeholder="例如：负责公司官网前端开发，做了很多优化，效果很好"></textarea>
          </div>
          <button class="btn btn-primary" :disabled="aiLoading" @click="aiOptimize">{{ aiLoading ? '优化中…' : '开始优化' }}</button>
          <div v-if="aiResult" class="ai-result">
            <pre>{{ aiResult }}</pre>
            <button class="btn btn-dark btn-sm" @click="applyAi">应用到个人总结</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 18px; margin-bottom: 16px; flex-wrap: wrap; }
.tpl-list { display: flex; gap: 10px; flex-wrap: wrap; }
.tpl {
  display: flex; align-items: center; gap: 10px; padding: 8px 14px 8px 8px;
  border: 1.5px solid var(--line); border-radius: 12px; cursor: pointer; transition: all .2s;
}
.tpl.on { border-color: var(--accent); background: var(--accent-soft); }
.tpl i { width: 30px; height: 40px; border-radius: 4px; flex: none; border: 1px solid var(--line); }
.tpl i.minimal { background: linear-gradient(#fff 30%, #f2f0ea 30%); }
.tpl i.business { background: linear-gradient(90deg, #23262B 35%, #fff 35%); }
.tpl i.creative { background: linear-gradient(135deg, var(--accent) 28%, #fff 28%); }
.tpl strong { display: block; font-size: 13px; }
.tpl small { color: var(--muted); font-size: 11.5px; }
.ops { display: flex; gap: 8px; flex-wrap: wrap; }

.resume-layout { display: flex; gap: 16px; align-items: flex-start; justify-content: center; }
.edit-panel { width: 320px; flex: none; position: sticky; top: 24px; max-height: 82vh; display: flex; flex-direction: column; }
.ep-tabs { display: flex; flex-wrap: wrap; gap: 4px; padding: 12px 12px 0; }
.ep-tabs button { padding: 5px 12px; border-radius: 8px; font-size: 12.5px; color: var(--ink-2); }
.ep-tabs button.on { background: var(--ink); color: #F5F2EA; }
.ep-body { padding: 14px; overflow-y: auto; }
.ep-item { border: 1px dashed var(--line); border-radius: 10px; padding: 10px; margin-bottom: 10px; display: flex; flex-direction: column; gap: 8px; }
.rm { align-self: flex-end; font-size: 12px; color: var(--rose); }

/* 简历纸张 */
.resume-paper { flex: 1; max-width: 760px; background: #fff; border-radius: 12px; padding: 48px 52px; box-shadow: var(--shadow-lg); border: 1px solid var(--line-2); }
.r-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; border-bottom: 2px solid var(--ink); padding-bottom: 18px; flex-wrap: wrap; }
.r-head h1 { font-size: 30px; font-weight: 800; }
.r-title { color: var(--ink-2); margin-top: 4px; }
.r-contact { display: flex; flex-direction: column; gap: 3px; font-size: 13px; color: var(--ink-2); text-align: right; }
.r-sec { margin-top: 22px; }
.r-sec h2 { font-size: 15px; font-weight: 700; letter-spacing: .12em; color: var(--accent-strong); margin-bottom: 10px; }
.r-item { margin-bottom: 12px; }
.r-line { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.r-line em { font-style: normal; color: var(--muted); font-size: 13px; }
.r-item p { color: var(--ink-2); font-size: 13.5px; margin-top: 4px; line-height: 1.75; }
.r-skills { display: flex; flex-wrap: wrap; gap: 8px; }
.r-skills span { border: 1px solid var(--line); padding: 3px 12px; border-radius: 999px; font-size: 12.5px; color: var(--ink-2); }

/* 模板变体 */
.resume-paper.business { border-top: 8px solid #23262B; }
.resume-paper.business .r-sec h2 { color: #23262B; }
.resume-paper.business .r-head { border-bottom-color: #23262B; }
.resume-paper.creative { border-top: 8px solid var(--accent); background: linear-gradient(180deg, #FFF8F3, #fff 30%); }
.resume-paper.creative .r-head h1 { color: var(--accent-strong); }

.ai-result { margin-top: 14px; border: 1px solid var(--line-2); border-radius: 12px; padding: 14px; background: var(--surface-2); }
.ai-result pre { white-space: pre-wrap; font-family: inherit; font-size: 13.5px; line-height: 1.7; margin-bottom: 10px; }

@media (max-width: 1080px) {
  .resume-layout { flex-direction: column; }
  .edit-panel { width: 100%; position: static; }
}
@media (max-width: 860px) { .resume-paper { padding: 28px 20px; } }

/* 打印样式：只输出简历 */
@media print {
  :deep(.sidebar), .no-print { display: none !important; }
  .resume-layout { display: block; }
  .resume-paper { box-shadow: none; border: none; border-radius: 0; max-width: none; padding: 10mm 4mm; }
  :global(.sidebar), :global(.tabbar), :global(.mobile-top), :global(.ai-fab), :global(.ai-panel) { display: none !important; }
  :global(.main-area) { padding: 0 !important; }
  :global(body) { background: #fff !important; }
}
</style>
