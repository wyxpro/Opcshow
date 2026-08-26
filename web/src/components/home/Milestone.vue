<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import PhotoPreview, { type PhotoItem } from './PhotoPreview.vue'

export interface MilestoneItem {
  id: number
  eventDate: number
  title: string
  description?: string
  image?: string
  tags?: string[]
}

const props = defineProps<{
  milestones?: MilestoneItem[]
}>()

const DEFAULT_MILESTONES: MilestoneItem[] = [
  { id: 1, eventDate: new Date('2017-06-01').getTime(), title: '进入站长圈，开启自我探索', description: '拥有了人生第一个属于自己的个人独立网站，开启了持续的自学与编程狂欢。', tags: ['起源', '独立站长'] },
  { id: 2, eventDate: new Date('2020-09-01').getTime(), title: '大学全栈深造与技能重构', description: '全面攻克 Vue、React、Node.js 与 Go，实现独立全栈闭环架构开发。', tags: ['全栈工程师', '技术突破'] },
  { id: 3, eventDate: new Date('2022-04-15').getTime(), title: '坐标浙江宁波，开启职业生涯', description: '正式踏入工业与商业软件研发领域，在宁波担任核心前端/全栈工程师。', tags: ['宁波', '职业发展'] },
  { id: 4, eventDate: new Date('2024-01-10').getTime(), title: '开源项目 ThriveX 发布', description: '将积累多年的精美全栈博客系统开源，获得广大独立站长与开发者好评。', tags: ['开源作品', 'ThriveX'] },
  { id: 5, eventDate: new Date('2026-08-01').getTime(), title: 'Opcshow 数字资产主页打造', description: '打造集可视化拖拽、AI 智能助手、知识库与生活动态于一体的个人旗舰系统。', tags: ['Opcshow', '数字自留地'] },
]

const rootRef = ref<HTMLElement | null>(null)
const scrollRef = ref<HTMLDivElement | null>(null)
const starsRef = ref<HTMLDivElement | null>(null)
const starsNearRef = ref<HTMLDivElement | null>(null)
const auroraRef = ref<HTMLDivElement | null>(null)

const viewportH = ref(800)
const hintHidden = ref(false)
const starsShadow = ref('')
const starsNearShadow = ref('')
const previewOpen = ref(false)
const previewIndex = ref(0)
const isActive = ref(false)

const dragState = ref({ isDown: false, startX: 0, scrollLeft: 0 })

const SIDE_PAD = 400
const CARD_SP = 560
const CARD_W = 300
const WAVE_AMP = 60
const CONN_GAP = 45
const WAVE_PERIOD = 1120
const CARD_H_ESTIMATE = 260
const WK = (2 * Math.PI) / WAVE_PERIOD
const WPHI = Math.PI / 2 - WK * SIDE_PAD

const activeMilestones = computed(() =>
  props.milestones && props.milestones.length > 0 ? props.milestones : DEFAULT_MILESTONES
)

const sortedEvents = computed(() =>
  [...activeMilestones.value].sort((a, b) => a.eventDate - b.eventDate || a.id - b.id)
)

const previewPhotos = computed<PhotoItem[]>(() =>
  sortedEvents.value
    .filter((event) => event.image)
    .map((event) => ({ id: `${event.id}`, url: event.image!, alt: event.title }))
)

function formatEventDate(value: number) {
  return new Date(value).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '.')
}

function extractYear(value: number) {
  return String(new Date(value).getFullYear())
}

function openPreview(id: number) {
  const index = previewPhotos.value.findIndex((photo) => photo.id === `${id}`)
  if (index < 0) return
  previewIndex.value = index
  previewOpen.value = true
}

const centerY = computed(() => Math.max(viewportH.value, 600) / 2)
const totalW = computed(() =>
  sortedEvents.value.length > 0 ? SIDE_PAD * 2 + CARD_SP * (sortedEvents.value.length - 1) : 1200
)

function buildWavePath(totalW: number, centerY: number, offsetY = 0) {
  const pts = 300
  let d = ''
  for (let i = 0; i <= pts; i++) {
    const x = (totalW / pts) * i
    const y = centerY + WAVE_AMP * Math.sin(WK * x + WPHI) + offsetY
    d += `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
  }
  return d
}

function buildStarsShadow(count = 100, opacity = 0.25, w = 1200, h = 800) {
  const shadows: string[] = []
  for (let i = 0; i < count; i++) {
    const ox = Math.round(Math.random() * w)
    const oy = Math.round(Math.random() * h)
    const op = (Math.random() * opacity + 0.05).toFixed(2)
    shadows.push(`${ox}px ${oy}px 1px rgba(255,255,255,${op})`)
  }
  return shadows.join(',')
}

const wavePath = computed(() => buildWavePath(totalW.value, centerY.value))
const waveEchoPath = computed(() => buildWavePath(totalW.value, centerY.value, 3))

const layoutItems = computed(() => {
  const waveY = (x: number) => centerY.value + WAVE_AMP * Math.sin(WK * x + WPHI)

  return sortedEvents.value.map((event, index) => {
    const x = SIDE_PAD + CARD_SP * index
    const dy = waveY(x)
    const isAbove = index % 2 === 0
    const delay = 1.5 + index * 0.35

    let cardTop: number
    let connTop: number
    let connHeight: number

    if (isAbove) {
      cardTop = dy - CONN_GAP - CARD_H_ESTIMATE
      connTop = cardTop + CARD_H_ESTIMATE
      connHeight = CONN_GAP
    } else {
      cardTop = dy + CONN_GAP
      connTop = dy
      connHeight = CONN_GAP
    }

    return { event, index, x, waveY: dy, isAbove, delay, cardTop, connTop, connHeight }
  })
})

function onScroll() {
  const sc = scrollRef.value
  if (!sc) return
  const sl = sc.scrollLeft
  if (starsRef.value) starsRef.value.style.transform = `translateX(${-sl * 0.05}px)`
  if (starsNearRef.value) starsNearRef.value.style.transform = `translateX(${-sl * 0.16}px)`
  if (auroraRef.value) auroraRef.value.style.transform = `translate3d(${-sl * 0.08}px,0,0) rotate(-8deg)`
  if (!hintHidden.value && sl > 60) hintHidden.value = true
}

let ro: ResizeObserver | null = null
let io: IntersectionObserver | null = null

onMounted(() => {
  const root = rootRef.value
  if (!root) return

  const syncSize = () => {
    const h = Math.max(root.clientHeight, 600)
    const w = Math.max(root.clientWidth, 1200)
    viewportH.value = h
    starsShadow.value = buildStarsShadow(100, 0.25, w, h)
    starsNearShadow.value = buildStarsShadow(45, 0.45, w, h)
  }

  syncSize()
  ro = new ResizeObserver(syncSize)
  ro.observe(root)

  io = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        isActive.value = true
        io?.disconnect()
      }
    },
    { threshold: 0.35 }
  )
  io.observe(root)

  const sc = scrollRef.value
  if (!sc) return

  const onMouseDown = (e: MouseEvent) => {
    dragState.value = { isDown: true, startX: e.pageX, scrollLeft: sc.scrollLeft }
    sc.classList.add('is-dragging')
  }

  const onMouseUp = () => {
    dragState.value.isDown = false
    sc.classList.remove('is-dragging')
  }

  const onMouseMove = (e: MouseEvent) => {
    if (!dragState.value.isDown) return
    e.preventDefault()
    sc.scrollLeft = dragState.value.scrollLeft - (e.pageX - dragState.value.startX) * 1.5
  }

  const onWheel = (e: WheelEvent) => {
    const delta = e.deltaY || e.deltaX
    if (!delta) return
    const maxScroll = sc.scrollWidth - sc.clientWidth
    const atStart = sc.scrollLeft <= 0
    const atEnd = sc.scrollLeft >= maxScroll - 1
    if ((atStart && delta < 0) || (atEnd && delta > 0)) return
    e.preventDefault()
    sc.scrollLeft += delta * 1.5
  }

  sc.addEventListener('mousedown', onMouseDown)
  window.addEventListener('mouseup', onMouseUp)
  window.addEventListener('mousemove', onMouseMove)
  sc.addEventListener('wheel', onWheel, { passive: false })
  sc.addEventListener('scroll', onScroll)
})

onUnmounted(() => {
  ro?.disconnect()
  io?.disconnect()
})
</script>

<template>
  <section
    ref="rootRef"
    id="milestone"
    data-section
    :class="[
      'milestone-page relative h-[100svh] w-full overflow-hidden bg-[#06060f] font-serif text-[#e8e4dc] selection:bg-[rgba(232,160,48,0.3)] selection:text-white',
      isActive ? 'is-active' : ''
    ]"
  >
    <div class="bg-mesh absolute inset-0 z-0" />
    <div class="pointer-events-none absolute z-1 size-[350px] rounded-full bg-[rgba(100,50,200,0.5)] opacity-20 blur-[80px] orb-1 left-[-100px] top-[-80px]" />
    <div class="pointer-events-none absolute z-1 size-[280px] rounded-full bg-[rgba(30,70,180,0.4)] opacity-20 blur-[80px] orb-2 bottom-[-60px] right-[-40px]" />
    <div class="pointer-events-none absolute z-1 size-[200px] rounded-full bg-[rgba(200,120,40,0.25)] opacity-20 blur-[80px] orb-3 left-[55%] top-[35%]" />

    <div ref="starsRef" class="stars pointer-events-none absolute left-0 top-0 z-1 size-px will-change-transform" :style="{ boxShadow: starsShadow }" />
    <div ref="starsNearRef" class="stars pointer-events-none absolute left-0 top-0 z-4 size-px opacity-70 drop-shadow-[0_0_6px_rgba(232,160,48,0.45)] stars-near" :style="{ boxShadow: starsNearShadow }" />
    <div ref="auroraRef" class="aurora-ribbon pointer-events-none absolute left-[-12vw] top-[18%] z-2 h-[42%] w-[135%] rotate-[-8deg] opacity-30 blur-3xl will-change-transform" />

    <div class="pointer-events-none absolute inset-0 z-2 bg-[radial-gradient(ellipse_at_50%_50%,transparent_35%,rgba(0,0,0,0.45)_100%)]" />
    <div class="grain pointer-events-none absolute inset-0 z-3 bg-size-[200px] bg-repeat opacity-[0.03]" />

    <!-- 标题头 -->
    <header :class="['page-header pointer-events-none absolute left-[40px] md:left-[80px] lg:left-[112px] top-[34px] z-[100] transition-[transform,opacity] duration-500 ease-out', hintHidden ? 'translate-y-[-10px] scale-[0.92] opacity-40' : '']">
      <h1 class="font-bold tracking-[0.08em] text-[#f6efe3] text-[clamp(34px,5vw,68px)] [text-shadow:0_0_28px_rgba(232,160,48,0.22)]">🏆 里程碑</h1>
    </header>

    <div ref="scrollRef" class="scroll-container relative z-10 h-full w-full cursor-grab overflow-x-auto overflow-y-hidden scrollbar-none active:cursor-grabbing">
      <div class="relative h-full min-h-[600px]" :style="{ width: `${totalW}px` }">
        <!-- SVG 波浪与光辉线 -->
        <svg class="pointer-events-none absolute left-0 top-0 overflow-visible" :width="totalW" :height="viewportH" :style="{ width: `${totalW}px`, height: '100%' }">
          <defs>
            <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="rgba(232,160,48,.06)" />
              <stop offset="15%" stop-color="rgba(232,160,48,.5)" />
              <stop offset="50%" stop-color="rgba(240,180,60,.7)" />
              <stop offset="85%" stop-color="rgba(232,160,48,.5)" />
              <stop offset="100%" stop-color="rgba(232,160,48,.06)" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="g" />
              <feMerge>
                <feMergeNode in="g" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <path :d="wavePath" class="wave-glow" />
          <path :d="wavePath" class="wave-main" />
          <path :d="waveEchoPath" class="wave-echo" />
          <path :d="wavePath" class="wave-comet" />
        </svg>

        <!-- 里程碑卡片与节点 -->
        <div v-for="item in layoutItems" :key="item.event.id">
          <!-- 背景年份水印 -->
          <div
            class="pointer-events-none absolute z-5 -translate-x-1/2 -translate-y-1/2 select-none font-serif text-[64px] font-normal italic text-white/5"
            :style="{ left: `${item.x}px`, top: `${item.isAbove ? item.waveY + 70 : item.waveY - 70}px` }"
          >
            {{ extractYear(item.event.eventDate) }}
          </div>

          <!-- 节点 Point -->
          <div class="timeline-dot absolute z-20 opacity-0" :style="{ left: `${item.x}px`, top: `${item.waveY}px`, animationDelay: `${item.delay}s` }">
            <div class="absolute left-[18px] top-[-28px] font-mono text-[10px] tracking-[0.12em] text-[rgba(255,236,170,0.5)] [text-shadow:0_0_20px_rgba(232,160,48,0.55)]">
              {{ String(item.index + 1).padStart(2, '0') }}
            </div>
            <div class="dot-orbit absolute inset-[-22px] rounded-full border border-[rgba(232,160,48,0.18)] border-b-transparent border-l-[rgba(255,236,170,0.75)]" />
            <div class="size-3 rounded-full bg-[linear-gradient(135deg,#f0c060,#d89828)] shadow-[0_0_15px_rgba(232,160,48,0.5),0_0_30px_rgba(232,160,48,0.15)]" />
            <div class="dot-ring absolute inset-[-8px] rounded-full border-[1.5px] border-[rgba(232,160,48,0.2)]" />
            <div class="dot-ring-outer absolute inset-[-16px] rounded-full border border-[rgba(232,160,48,0.08)]" />
          </div>

          <!-- 连接线 Connector -->
          <div
            :class="['connector absolute z-15 w-px opacity-0', item.isAbove ? 'from-above' : 'from-below']"
            :style="{ left: `${item.x}px`, top: `${item.connTop}px`, height: `${item.connHeight}px`, animationDelay: `${item.delay + 0.1}s` }"
          />

          <!-- 玻璃拟态事件卡片 Glass Card -->
          <div
            :class="['glass-card visible absolute z-25 w-[300px] overflow-hidden rounded-[18px] border border-white/10 bg-[linear-gradient(145deg,rgba(255,255,255,0.075),rgba(255,255,255,0.026))] opacity-0 shadow-[0_4px_24px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.05)] backdrop-blur-3xl transition-[transform,box-shadow] duration-700 ease-out hover:!-translate-y-[7px] hover:!scale-[1.018]', item.isAbove ? 'slide-down' : 'slide-up']"
            :style="{ left: `${item.x - CARD_W / 2}px`, top: `${item.cardTop}px`, width: `${CARD_W}px`, animationDelay: `${item.delay + 0.2}s` }"
          >
            <div class="card-image-wrap relative -mb-px overflow-hidden">
              <button
                v-if="item.event.image"
                type="button"
                class="group relative block w-full cursor-pointer appearance-none overflow-hidden border-0 bg-transparent p-0 outline-none"
                @click="openPreview(item.event.id)"
              >
                <img :src="item.event.image" :alt="item.event.title" class="card-image block h-[140px] w-full object-cover transition-transform duration-750 ease-out group-hover:scale-105" />
                <span class="absolute inset-0 z-3 grid translate-y-2 place-items-center bg-[rgba(6,6,15,0.36)] text-xs tracking-[0.18em] text-white/85 opacity-0 transition-[opacity,transform] duration-500 ease-out group-hover:translate-y-0 group-hover:opacity-100">点击预览</span>
              </button>
              <div v-else class="card-image h-[140px] w-full bg-[linear-gradient(135deg,rgba(50,30,80,0.4),rgba(30,40,70,0.4))]" />
            </div>

            <div class="relative z-2 bg-[rgba(14,12,28,0.72)] px-4 pb-3 pt-[15px]">
              <div class="mb-1 font-mono text-[10.5px] tracking-[0.12em] text-[rgba(232,160,48,0.65)]">{{ formatEventDate(item.event.eventDate) }}</div>
              <div class="mb-1.5 font-serif text-base font-semibold leading-[1.35] text-[#f0ece4]">{{ item.event.title }}</div>
              <div v-if="item.event.description" class="mb-2.5 line-clamp-2 overflow-hidden text-xs leading-[1.75] text-[rgba(228,224,216,0.5)]">{{ item.event.description }}</div>
              <div class="flex items-center justify-between">
                <div class="flex flex-wrap gap-[5px]">
                  <span v-for="tag in (item.event.tags ?? [])" :key="tag" class="rounded-[20px] border border-white/10 bg-white/5 px-[7px] py-0.5 font-mono text-[9.5px] tracking-wider text-white/40">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 拖拽提示 -->
    <div :class="['pointer-events-none absolute bottom-6 left-1/2 z-[100] flex -translate-x-1/2 items-center gap-2 font-mono text-[10.5px] tracking-[0.15em] text-white/20 transition-opacity duration-1000', hintHidden ? 'opacity-0' : '']">
      <span class="arr">←</span>
      <span>拖拽探索里程碑</span>
      <span class="arr">→</span>
    </div>

    <PhotoPreview
      :open="previewOpen"
      :photos="previewPhotos"
      :index="previewIndex"
      @close="previewOpen = false"
      @change="(idx) => (previewIndex = idx)"
    />
  </section>
</template>
