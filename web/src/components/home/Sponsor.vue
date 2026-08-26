<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const sectionRef = ref<HTMLElement | null>(null)
let ctx: gsap.Context | null = null

const LOGO_SRC = 'https://www.crash.work/themes/web/www/upload/local685e578aed0a9.png'
const SITE_URL = 'https://www.crash.work/'
const SPECS = ['4H', '8G', '500M'] as const

onMounted(() => {
  gsap.registerPlugin(ScrollTrigger)
  const section = sectionRef.value
  if (!section) return

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const stage = section.querySelector<HTMLElement>('[data-sponsor-stage]')
  const slots = section.querySelectorAll<HTMLElement>('[data-sponsor-slot]')
  const beam = section.querySelectorAll<HTMLElement>('[data-sponsor-beam]')

  ctx = gsap.context(() => {
    if (prefersReduced) {
      gsap.set([stage, ...Array.from(slots), ...Array.from(beam)], { autoAlpha: 1, y: 0, scale: 1 })
      return
    }

    gsap.set(stage, { autoAlpha: 0, y: 80, scale: 0.88 })
    gsap.set(slots, { autoAlpha: 0, y: 48, scale: 0.94 })
    gsap.set(beam, { scaleX: 0, autoAlpha: 0 })

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        start: 'top 68%',
        end: 'top 28%',
        scrub: 0.55,
      },
    })

    tl.to(stage, { autoAlpha: 1, y: 0, scale: 1, ease: 'power3.out', duration: 1 }, 0)
      .to(slots, { autoAlpha: 1, y: 0, scale: 1, stagger: 0.08, ease: 'power3.out', duration: 0.7 }, 0.18)
      .to(beam, { scaleX: 1, autoAlpha: 1, stagger: 0.06, ease: 'power2.out', duration: 0.55 }, 0.35)
  }, section)
})

onUnmounted(() => {
  ctx?.revert()
})
</script>

<template>
  <section
    ref="sectionRef"
    id="sponsor"
    data-section
    class="sponsor relative min-h-[100svh] overflow-hidden px-10 py-24 md:px-20 md:py-32 lg:px-28"
  >
    <div class="sponsor-aurora pointer-events-none absolute inset-0" />
    <div class="sponsor-grid pointer-events-none absolute inset-0 opacity-[0.18]" />
    <div class="pointer-events-none absolute left-1/2 top-1/2 h-[70vmin] w-[70vmin] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(83,157,253,0.22),transparent_68%)] blur-3xl" />

    <!-- 水印 -->
    <p
      aria-hidden="true"
      class="sponsor-watermark pointer-events-none absolute left-1/2 top-[6%] z-0 -translate-x-1/2 select-none whitespace-nowrap font-black leading-none tracking-[-0.08em] text-[24vw] text-white/[0.045] md:top-[2%] md:text-[18vw]"
    >
      SPONSOR
    </p>

    <div class="relative z-10 mx-auto flex max-w-[1380px] flex-col items-center text-center">
      <p data-reveal class="mb-5 text-[11px] font-semibold uppercase tracking-[0.4em] text-[#539dfd]">
        Exclusive Partners
      </p>

      <h2
        data-section-title
        class="text-balance text-5xl font-black leading-[1.05] tracking-[-0.06em] text-white md:text-7xl lg:text-[6.5rem]"
      >
        一路<em class="font-normal not-italic text-[#539dfd]">前行</em>
      </h2>

      <p data-reveal class="mt-6 max-w-xl text-sm leading-7 text-white/62 md:text-base md:leading-8">
        感谢每一位同行者
      </p>

      <div class="relative mt-16 w-full max-w-6xl lg:mt-20">
        <div
          data-sponsor-beam
          aria-hidden="true"
          class="sponsor-beam pointer-events-none absolute left-[8%] right-[8%] top-[46%] hidden h-px origin-left bg-[linear-gradient(90deg,transparent,rgba(83,157,253,0.55),transparent)] lg:block"
        />

        <div class="grid items-center gap-6 lg:grid-cols-[0.85fr_1.3fr_0.85fr] lg:gap-4">
          <!-- 虚位以待 1 -->
          <div
            data-sponsor-slot
            class="sponsor-slot relative flex min-h-[240px] flex-col items-center justify-center gap-4 overflow-hidden rounded-[28px] border border-dashed border-white/18 bg-white/[0.02] px-5 py-10 lg:min-h-[320px]"
          >
            <div aria-hidden="true" class="sponsor-slot-shimmer pointer-events-none absolute inset-0" />
            <span class="relative z-10 text-[11px] font-semibold uppercase tracking-[0.28em] text-white/40">Token 赞助商</span>
            <span class="sponsor-vacant relative z-10 text-2xl font-light tracking-[0.2em] text-white/25 md:text-3xl">虚位以待</span>
            <span class="relative z-10 text-[10px] font-bold uppercase tracking-[0.32em] text-white/18">Coming Soon</span>
          </div>

          <!-- 独家赞助商卡片 -->
          <a
            :href="SITE_URL"
            target="_blank"
            rel="noreferrer"
            data-sponsor-stage
            aria-label="访问破碎工坊云官网"
            class="sponsor-stage group relative cursor-pointer rounded-[32px] border border-[#539dfd]/35 bg-[linear-gradient(160deg,rgba(16,28,48,0.95),rgba(8,12,20,0.92))] px-6 py-10 shadow-[0_0_0_1px_rgba(83,157,253,0.12),0_30px_100px_rgba(0,0,0,0.55),0_0_80px_rgba(83,157,253,0.22)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#539dfd]/70 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050608] md:px-10 md:py-12"
          >
            <div aria-hidden="true" class="sponsor-ring sponsor-ring--outer" />
            <div aria-hidden="true" class="sponsor-ring sponsor-ring--inner" />
            <div aria-hidden="true" class="sponsor-flare" />

            <span class="relative z-10 inline-flex items-center gap-2 rounded-full border border-[#539dfd]/35 bg-[#539dfd]/10 px-3.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.28em] text-[#8ec5ff]">
              <span class="sponsor-live-dot h-1.5 w-1.5 rounded-full bg-[#63d47f]" />
              服务器独家赞助
            </span>

            <div class="relative z-10 mx-auto mt-8 flex h-[88px] w-full max-w-[320px] items-center justify-center px-6 md:h-[100px]">
              <div class="relative h-12 w-full md:h-14">
                <img :src="LOGO_SRC" alt="破碎工坊云" class="h-full w-full object-contain" />
              </div>
            </div>

            <p class="relative z-10 mt-6 text-sm font-medium tracking-wide text-white/70 md:text-base">
              赞助本站运行
            </p>

            <div class="relative z-10 mt-4 flex flex-wrap items-center justify-center gap-2.5">
              <span
                v-for="spec in SPECS"
                :key="spec"
                class="sponsor-spec rounded-full border border-[#539dfd]/30 bg-[#539dfd]/12 px-4 py-2 font-mono text-sm font-bold tracking-[0.12em] text-[#b7d9ff] md:text-base"
              >
                {{ spec }}
              </span>
              <span class="rounded-full border border-white/12 bg-white/[0.04] px-4 py-2 text-sm font-semibold tracking-wide text-white/55">
                服务器
              </span>
            </div>

            <span class="relative z-10 mt-8 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.28em] text-[#539dfd]">
              访问官网
              <svg viewBox="0 0 24 24" class="h-4 w-4 fill-none stroke-current stroke-2 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"><path d="M7 17L17 7M17 7H7M17 7V17" /></svg>
            </span>
          </a>

          <!-- 虚位以待 2 -->
          <div
            data-sponsor-slot
            class="sponsor-slot relative flex min-h-[240px] flex-col items-center justify-center gap-4 overflow-hidden rounded-[28px] border border-dashed border-white/18 bg-white/[0.02] px-5 py-10 lg:min-h-[320px]"
          >
            <div aria-hidden="true" class="sponsor-slot-shimmer pointer-events-none absolute inset-0" />
            <span class="relative z-10 text-[11px] font-semibold uppercase tracking-[0.28em] text-white/40">Token 赞助商</span>
            <span class="sponsor-vacant relative z-10 text-2xl font-light tracking-[0.2em] text-white/25 md:text-3xl">虚位以待</span>
            <span class="relative z-10 text-[10px] font-bold uppercase tracking-[0.32em] text-white/18">Coming Soon</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
