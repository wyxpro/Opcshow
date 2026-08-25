<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const KEYWORDS = ['热爱', '全局', '全栈', '架构师'] as const

const active = ref(0)
const kwHover = ref<number | null>(null)
const reduceMotion = ref(false)

const sectionRef = ref<HTMLElement | null>(null)
const parasRef = ref<(HTMLElement | null)[]>([])
const keywordsRef = ref<(HTMLButtonElement | null)[]>([])
const watermarkRef = ref<HTMLElement | null>(null)
const progressRef = ref<HTMLElement | null>(null)

let pinTrigger: ScrollTrigger | null = null
let ctx: gsap.Context | null = null

const STEP_COUNT = 4
const LAST_STEP = STEP_COUNT - 1
const SCROLL_SCREENS = LAST_STEP + 0.25

function progressToStep(progress: number) {
  const storyProgress = Math.min(1, (progress * SCROLL_SCREENS) / LAST_STEP)
  return Math.min(LAST_STEP, Math.max(0, Math.round(storyProgress * LAST_STEP)))
}

function stepToProgress(step: number) {
  return (step / LAST_STEP) * (LAST_STEP / SCROLL_SCREENS)
}

function goToStep(index: number) {
  const next = Math.min(LAST_STEP, Math.max(0, index))
  active.value = next
  kwHover.value = null

  if (reduceMotion.value || !pinTrigger) return

  const progress = LAST_STEP === 0 ? 0 : stepToProgress(next)
  const top = pinTrigger.start + (pinTrigger.end - pinTrigger.start) * progress

  window.scrollTo({
    top,
    behavior: 'smooth',
  })
}

watch(active, (newVal) => {
  if (reduceMotion.value) return

  const paras = parasRef.value.filter(Boolean) as HTMLElement[]
  const keywords = keywordsRef.value.filter(Boolean) as HTMLButtonElement[]
  const watermark = watermarkRef.value
  const isLg = window.matchMedia('(min-width: 1024px)').matches

  paras.forEach((para, index) => {
    const on = index === newVal
    gsap.to(para, {
      autoAlpha: on ? 1 : 0,
      y: on ? 0 : index < newVal ? -18 : 24,
      pointerEvents: on ? 'auto' : 'none',
      duration: 0.5,
      ease: 'power3.out',
      overwrite: 'auto',
    })
  })

  keywords.forEach((kw, index) => {
    const on = index === newVal
    const soft = kwHover.value === index && !on
    gsap.to(kw, {
      x: on && isLg ? -14 : 0,
      scale: on ? 1.08 : soft ? 1.02 : 0.94,
      opacity: on ? 1 : soft ? 0.55 : 0.28,
      duration: 0.35,
      ease: 'power2.out',
      overwrite: 'auto',
    })
  })

  if (watermark) {
    watermark.textContent = KEYWORDS[newVal]
    gsap.to(watermark, {
      autoAlpha: 1,
      duration: 0.35,
      ease: 'power2.out',
      overwrite: 'auto',
    })
  }
})

function handleKeydown(e: KeyboardEvent) {
  if (reduceMotion.value || !pinTrigger?.isActive) return
  const cur = active.value
  if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === 'PageDown') {
    if (cur >= LAST_STEP) return
    e.preventDefault()
    goToStep(cur + 1)
  } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft' || e.key === 'PageUp') {
    if (cur <= 0) return
    e.preventDefault()
    goToStep(cur - 1)
  }
}

onMounted(() => {
  reduceMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  gsap.registerPlugin(ScrollTrigger)

  const section = sectionRef.value
  if (!section) return

  ctx = gsap.context(() => {
    const paras = parasRef.value.filter(Boolean) as HTMLElement[]

    if (reduceMotion.value) {
      gsap.set(paras, { autoAlpha: 1, y: 0 })
      return
    }

    gsap.set(paras, { autoAlpha: 0, y: 24, pointerEvents: 'none' })
    if (paras[0]) gsap.set(paras[0], { autoAlpha: 1, y: 0, pointerEvents: 'auto' })

    pinTrigger = ScrollTrigger.create({
      id: 'story-pin',
      trigger: section,
      start: 'top top',
      end: () => `+=${Math.round(window.innerHeight * SCROLL_SCREENS)}`,
      pin: true,
      scrub: 0.45,
      anticipatePin: 1,
      invalidateOnRefresh: true,
      onUpdate: (self) => {
        const index = progressToStep(self.progress)
        if (progressRef.value) {
          const storyProgress = Math.min(1, (self.progress * SCROLL_SCREENS) / LAST_STEP)
          gsap.set(progressRef.value, { scaleY: storyProgress })
        }
        if (active.value !== index) {
          active.value = index
        }
      },
    })
  }, section)

  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  pinTrigger = null
  ctx?.revert()
})
</script>

<template>
  <section
    ref="sectionRef"
    id="story"
    data-section
    class="relative flex min-h-[100svh] items-center overflow-hidden px-6 py-20 md:px-12 md:py-24 lg:px-16"
  >
    <!-- 光亮色块遮罩 -->
    <div class="pointer-events-none absolute -left-1/4 top-0 h-[70%] w-[80%] bg-[radial-gradient(ellipse_at_center,rgba(215,163,91,0.16),transparent_62%)]" />
    <div class="pointer-events-none absolute -right-1/4 bottom-0 h-[55%] w-[70%] bg-[radial-gradient(ellipse_at_center,rgba(83,157,253,0.12),transparent_65%)]" />

    <!-- 巨型背影文字 -->
    <div aria-hidden="true" class="pointer-events-none absolute left-1/2 top-[10%] z-0 -translate-x-1/2 select-none md:top-[6%]">
      <p
        ref="watermarkRef"
        class="whitespace-nowrap font-black leading-none tracking-[-0.08em] text-[28vw] text-white/[0.04] md:text-[20vw]"
      >
        {{ KEYWORDS[active] }}
      </p>
    </div>

    <div class="relative z-10 mx-auto w-full max-w-7xl">
      <div class="grid items-center gap-12 lg:grid-cols-[1.15fr_0.85fr] lg:gap-10 xl:gap-16">
        <!-- 段落切换内容 -->
        <div :class="reduceMotion ? 'relative space-y-12' : 'relative min-h-[220px] md:min-h-[280px] lg:min-h-[320px]'">
          <span
            v-if="!reduceMotion"
            aria-hidden="true"
            class="pointer-events-none absolute bottom-2 left-0 top-2 hidden w-px overflow-hidden bg-white/10 md:block"
          >
            <span
              ref="progressRef"
              class="absolute inset-x-0 top-0 h-full origin-top scale-y-0 bg-[linear-gradient(180deg,#d7a35b,rgba(83,157,253,0.8))]"
            />
          </span>

          <!-- 01 -->
          <p
            :ref="(el) => (parasRef[0] = el as HTMLElement)"
            class="story-para max-w-3xl pl-0 text-[clamp(1.4rem,2.7vw,2.4rem)] font-light leading-[1.4] tracking-[-0.02em] text-white/85 md:pl-8"
            :class="reduceMotion ? 'relative' : 'absolute inset-x-0 top-0'"
          >
            <span aria-hidden="true" class="mb-4 block font-mono text-[11px] font-semibold tracking-[0.28em] text-[#d7a35b]">
              01 / 04
            </span>
            对于很多人来说写代码是一件 <em>痛苦不堪</em> 的事情，
            <br class="hidden md:block" />
            而我不一样，这正是我的 <em>爱好</em>。
          </p>

          <!-- 02 -->
          <p
            :ref="(el) => (parasRef[1] = el as HTMLElement)"
            class="story-para max-w-3xl pl-0 text-[clamp(1.4rem,2.7vw,2.4rem)] font-light leading-[1.4] tracking-[-0.02em] text-white/85 md:pl-8"
            :class="reduceMotion ? 'relative' : 'absolute inset-x-0 top-0'"
          >
            <span aria-hidden="true" class="mb-4 block font-mono text-[11px] font-semibold tracking-[0.28em] text-[#d7a35b]">
              02 / 04
            </span>
            所谓：
            <strong>“不谋全局者，不足谋一域”</strong>
            <br class="hidden md:block" />
            只专注一个领域，是无法做出一个完整的项目。
          </p>

          <!-- 03 -->
          <p
            :ref="(el) => (parasRef[2] = el as HTMLElement)"
            class="story-para max-w-3xl pl-0 text-[clamp(1.4rem,2.7vw,2.4rem)] font-light leading-[1.4] tracking-[-0.02em] text-white/85 md:pl-8"
            :class="reduceMotion ? 'relative' : 'absolute inset-x-0 top-0'"
          >
            <span aria-hidden="true" class="mb-4 block font-mono text-[11px] font-semibold tracking-[0.28em] text-[#d7a35b]">
              03 / 04
            </span>
            如果只会前端，做出来的项目是 <em>没有灵魂</em> 的项目；
            <br class="hidden md:block" />
            只会后端，连界面都看不到又能有什么意义。
          </p>

          <!-- 04 -->
          <p
            :ref="(el) => (parasRef[3] = el as HTMLElement)"
            class="story-para max-w-3xl pl-0 text-[clamp(1.4rem,2.7vw,2.4rem)] font-light leading-[1.4] tracking-[-0.02em] text-white/85 md:pl-8"
            :class="reduceMotion ? 'relative' : 'absolute inset-x-0 top-0'"
          >
            <span aria-hidden="true" class="mb-4 block font-mono text-[11px] font-semibold tracking-[0.28em] text-[#d7a35b]">
              04 / 04
            </span>
            我想具备的是能够 <em>一个人完成整个项目研发</em> 的能力，
            <br class="hidden md:block" />
            因此，我踏入了 <strong>全栈工程师</strong> 的探索之路。
          </p>
        </div>

        <!-- 关键词侧栏按键 -->
        <div class="flex flex-wrap items-end gap-x-5 gap-y-1 lg:flex-col lg:items-start lg:gap-1">
          <button
            v-for="(word, index) in KEYWORDS"
            :key="word"
            type="button"
            :ref="(el) => (keywordsRef[index] = el as HTMLButtonElement)"
            @click="goToStep(index)"
            @mouseenter="kwHover = index"
            @mouseleave="kwHover = null"
            :class="[
              'story-keyword origin-left cursor-pointer border-0 bg-transparent p-0 text-left font-light italic leading-[0.92] tracking-[-0.05em]',
              active === index ? 'story-keyword--active' : ''
            ]"
          >
            {{ word }}
          </button>
        </div>
      </div>

      <!-- 底栏圆点进度条 -->
      <div class="mt-10 flex items-center gap-4 md:mt-14">
        <div class="flex items-center gap-2" role="tablist">
          <button
            v-for="(word, index) in KEYWORDS"
            :key="word"
            type="button"
            role="tab"
            :aria-selected="active === index"
            @click="goToStep(index)"
            :class="[
              'h-1.5 cursor-pointer rounded-full transition-all duration-300',
              active === index ? 'w-7 bg-[#d7a35b]' : 'w-1.5 bg-white/25 hover:bg-white/45'
            ]"
          />
        </div>
        <p class="text-[11px] uppercase tracking-[0.24em] text-white/35">
          滚动翻页 · {{ active + 1 }}/4 · {{ KEYWORDS[active] }}
        </p>
      </div>
    </div>
  </section>
</template>
