<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const sectionRef = ref<HTMLElement | null>(null)
const peakRef = ref<HTMLElement | null>(null)
const linesRef = ref<HTMLElement | null>(null)
const tailRef = ref<HTMLElement | null>(null)
let ctx: gsap.Context | null = null

const VIDEO_SRC =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260510_060007_60275ce7-030c-4668-a160-8f364ec537d3.mp4'

onMounted(() => {
  gsap.registerPlugin(ScrollTrigger)
  const section = sectionRef.value
  const peak = peakRef.value
  const lines = linesRef.value
  const tail = tailRef.value
  if (!section || !peak || !lines || !tail) return

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  ctx = gsap.context(() => {
    if (prefersReduced) {
      gsap.set([peak, ...Array.from(lines.children), tail], { autoAlpha: 1, y: 0, scale: 1 })
      return
    }

    gsap.set(peak, { autoAlpha: 0, scale: 2.6, y: 100 })
    gsap.set(lines.children, { autoAlpha: 0, y: 56 })
    gsap.set(tail, { autoAlpha: 0, y: 40 })

    gsap
      .timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top 72%',
          end: 'top 16%',
          scrub: 0.55,
        },
      })
      .to(peak, { autoAlpha: 1, scale: 1, y: 0, ease: 'power3.out', duration: 1 }, 0)
      .to(
        Array.from(lines.children),
        { autoAlpha: 1, y: 0, stagger: 0.1, ease: 'power3.out', duration: 0.65 },
        0.22
      )
      .to(tail, { autoAlpha: 1, y: 0, ease: 'power3.out', duration: 0.6 }, 0.45)
  }, section)
})

onUnmounted(() => {
  ctx?.revert()
})
</script>

<template>
  <section
    ref="sectionRef"
    id="quote"
    data-section
    class="relative min-h-[100svh] overflow-hidden"
  >
    <div data-parallax class="absolute inset-[-10%] will-change-transform">
      <video
        :src="VIDEO_SRC"
        autoplay
        muted
        loop
        playsinline
        preload="metadata"
        aria-label="登顶山峰的向往"
        class="quote-video h-full w-full object-cover"
      />
    </div>

    <!-- 渐变与遮罩 -->
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(5,6,8,0.78)_0%,rgba(5,6,8,0.22)_34%,rgba(5,6,8,0.45)_62%,rgba(5,6,8,0.97)_100%)]" />
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_18%,rgba(5,6,8,0.72)_100%)]" />
    <div class="pointer-events-none absolute inset-x-0 top-0 h-[18%] bg-[linear-gradient(180deg,rgba(5,6,8,0.95),transparent)]" />
    <div class="pointer-events-none absolute inset-x-0 bottom-0 h-[28%] bg-[linear-gradient(0deg,rgba(5,6,8,0.98),transparent)]" />
    <div class="pointer-events-none absolute -left-1/4 top-1/4 h-[55%] w-[70%] bg-[radial-gradient(ellipse_at_center,rgba(215,163,91,0.22),transparent_68%)]" />
    <div class="pointer-events-none absolute -right-1/5 bottom-1/5 h-[48%] w-[55%] bg-[radial-gradient(ellipse_at_center,rgba(159,232,208,0.12),transparent_68%)]" />

    <!-- 水印 -->
    <p
      aria-hidden="true"
      class="quote-watermark pointer-events-none absolute left-1/2 top-[6%] z-[1] -translate-x-1/2 select-none whitespace-nowrap font-black leading-none tracking-[-0.08em] text-[26vw] text-white/[0.07] md:top-[2%] md:text-[20vw]"
    >
      SUMMIT
    </p>

    <div class="relative z-10 flex min-h-[100svh] flex-col justify-center px-4 py-24 md:px-8 md:py-28">
      <div class="mx-auto w-full max-w-7xl text-center">
        <blockquote class="mx-auto max-w-6xl">
          <div ref="linesRef" class="space-y-3 md:space-y-4">
            <p class="text-xl font-medium tracking-[-0.03em] text-white/55 md:text-3xl lg:text-4xl">
              半山腰风景很美，
            </p>
            <p class="text-xl font-medium tracking-[-0.03em] text-white/55 md:text-3xl lg:text-4xl">
              然而我还是更想到
            </p>
          </div>

          <span
            ref="peakRef"
            class="quote-peak mt-2 block font-black leading-[0.88] tracking-[-0.08em] text-[#d7a35b] md:mt-4"
          >
            山顶
          </span>

          <p
            ref="tailRef"
            class="mt-4 text-2xl font-black tracking-[-0.05em] text-white md:mt-6 md:text-5xl lg:text-6xl"
          >
            去看看。
          </p>
        </blockquote>
      </div>
    </div>
  </section>
</template>
