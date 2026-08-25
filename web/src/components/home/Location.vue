<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const sectionRef = ref<HTMLElement | null>(null)
const mapRef = ref<HTMLDivElement | null>(null)
const pinRef = ref<HTMLDivElement | null>(null)
let ctx: gsap.Context | null = null

const COORDS = {
  lat: '29.8683° N',
  lng: '121.5440° E',
} as const

onMounted(() => {
  gsap.registerPlugin(ScrollTrigger)
  const section = sectionRef.value
  const map = mapRef.value
  const pin = pinRef.value
  if (!section || !map || !pin) return

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  ctx = gsap.context(() => {
    if (prefersReduced) {
      gsap.set(map, { scale: 1 })
      gsap.set(pin, { autoAlpha: 1, y: 0, scale: 1 })
      return
    }

    gsap.set(map, { scale: 1.28 })
    gsap.set(pin, { autoAlpha: 0, y: -120, scale: 0.4 })

    gsap
      .timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top 70%',
          end: 'top 18%',
          scrub: 0.65,
        },
      })
      .to(map, { scale: 1, ease: 'none', duration: 1 }, 0)
      .to(pin, { autoAlpha: 1, y: 0, scale: 1, ease: 'power2.out', duration: 0.55 }, 0.35)
  }, section)
})

onUnmounted(() => {
  ctx?.revert()
})
</script>

<template>
  <section
    ref="sectionRef"
    id="location"
    data-section
    class="relative min-h-[100svh] overflow-hidden"
  >
    <!-- 宁波 OpenStreetMap 嵌入地图 -->
    <div ref="mapRef" class="absolute inset-[-6%] will-change-transform">
      <iframe
        title="宁波地图"
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade"
        src="https://www.openstreetmap.org/export/embed.html?bbox=121.35%2C29.70%2C122.15%2C30.15&amp;layer=mapnik&amp;marker=29.922533%2C121.853829"
        class="location-map h-full w-full border-0 grayscale-[0.7] brightness-[0.55] contrast-[1.2] saturate-[0.35]"
      />
    </div>

    <!-- 渐变遮罩层 -->
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(5,6,8,0.82)_0%,rgba(5,6,8,0.35)_38%,rgba(5,6,8,0.55)_68%,rgba(5,6,8,0.94)_100%)]" />
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_22%,rgba(5,6,8,0.72)_100%)]" />
    <div class="pointer-events-none absolute -left-1/4 top-0 h-[55%] w-[70%] bg-[radial-gradient(ellipse_at_center,rgba(159,232,208,0.14),transparent_65%)]" />
    <div class="pointer-events-none absolute -right-1/5 bottom-1/4 h-[45%] w-[55%] bg-[radial-gradient(ellipse_at_center,rgba(215,163,91,0.12),transparent_68%)]" />

    <!-- 巨幅水印背景字 -->
    <p
      aria-hidden="true"
      class="pointer-events-none absolute left-1/2 top-[10%] z-[1] -translate-x-1/2 select-none whitespace-nowrap font-black leading-none tracking-[-0.08em] text-[22vw] text-white/[0.05] md:top-[6%] md:text-[16vw]"
    >
      NINGBO
    </p>

    <!-- 地图雷达 Pin 标识 -->
    <div
      ref="pinRef"
      class="pointer-events-none absolute left-[58%] top-[46%] z-[2] -translate-x-1/2 -translate-y-1/2 md:left-[62%] md:top-[44%]"
    >
      <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <span class="location-ring location-ring--1 absolute left-1/2 top-1/2 h-28 w-28 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#9fe8d0]/50 md:h-40 md:w-40" />
        <span class="location-ring location-ring--2 absolute left-1/2 top-1/2 h-28 w-28 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#9fe8d0]/40 md:h-40 md:w-40" />
        <span class="location-ring location-ring--3 absolute left-1/2 top-1/2 h-28 w-28 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#d7a35b]/35 md:h-40 md:w-40" />
      </div>
      <div class="relative flex flex-col items-center">
        <span class="location-pin-core mb-2 flex h-11 w-11 items-center justify-center rounded-full bg-[#9fe8d0] text-[#050608] md:h-12 md:w-12">
          <svg viewBox="0 0 24 24" class="h-6 w-6 fill-none stroke-current stroke-2"><path d="M12 21s-6-4.35-6-10a6 6 0 1 1 12 0c0 5.65-6 10-6 10z" /><circle cx="12" cy="11" r="2.5" /></svg>
        </span>
        <span class="rounded-full bg-[#050608]/90 px-3.5 py-1.5 text-[11px] font-bold uppercase tracking-[0.16em] text-white backdrop-blur-sm">
          Ningbo · 宁波
        </span>
      </div>
    </div>

    <!-- 文案标题与经纬度 -->
    <div class="relative z-10 flex min-h-[100svh] flex-col justify-end px-6 pb-32 pt-28 md:px-12 md:pb-44 lg:px-16 lg:pb-52">
      <div class="mx-auto w-full max-w-7xl">
        <h2
          data-section-title
          class="max-w-5xl text-balance text-5xl font-black leading-[1.05] tracking-[-0.06em] text-white md:text-7xl lg:text-[6.5rem]"
        >
          目前我在
          <em class="font-normal not-italic text-[#9fe8d0]">浙江</em>
          <em class="font-normal not-italic text-[#d7a35b]">宁波</em>
          <br />
          从事前端开发
        </h2>

        <div
          data-reveal
          class="mt-10 flex flex-wrap items-center gap-x-8 gap-y-3 border-t border-white/12 pt-6 font-mono text-[11px] uppercase tracking-[0.2em] text-white/45 md:mt-12 md:gap-x-12"
        >
          <span>
            LAT <strong class="ml-2 font-semibold text-[#9fe8d0]">{{ COORDS.lat }}</strong>
          </span>
          <span>
            LNG <strong class="ml-2 font-semibold text-[#d7a35b]">{{ COORDS.lng }}</strong>
          </span>
          <span class="text-white/55">East China · Frontend</span>
        </div>
      </div>
    </div>
  </section>
</template>
