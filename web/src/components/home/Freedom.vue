<script setup lang="ts">
const VIDEO_SRC =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260602_150901_c45b90ec-18d7-42ff-90e2-b95d7109e330.mp4'

const DESTINATIONS = [
  '冰岛',
  '挪威',
  '日本',
  '新西兰',
  '瑞士',
  '加拿大',
  '智利',
  '摩洛哥',
  '意大利',
  '阿拉斯加',
  '西藏',
  '巴塔哥尼亚',
] as const

const track = [...DESTINATIONS, ...DESTINATIONS]
</script>

<template>
  <section id="freedom" data-section class="relative min-h-[100svh] overflow-hidden">
    <div data-parallax class="absolute inset-[-8%] will-change-transform">
      <video
        :src="VIDEO_SRC"
        autoplay
        muted
        loop
        playsinline
        preload="metadata"
        aria-label="环游世界的向往"
        class="freedom-video h-full w-full object-cover"
      />
    </div>

    <!-- 渐变底色遮罩 -->
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(5,6,8,0.55)_0%,rgba(5,6,8,0.18)_38%,rgba(5,6,8,0.72)_78%,rgba(5,6,8,0.96)_100%)]" />
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_28%,rgba(5,6,8,0.55)_100%)]" />
    <div class="pointer-events-none absolute -left-1/4 top-1/3 h-[50%] w-[70%] bg-[radial-gradient(ellipse_at_center,rgba(83,157,253,0.18),transparent_68%)]" />

    <p
      aria-hidden="true"
      class="pointer-events-none absolute left-1/2 top-[12%] z-[1] -translate-x-1/2 select-none whitespace-nowrap text-[22vw] font-black leading-none tracking-[-0.08em] text-white/[0.06] md:top-[8%] md:text-[18vw]"
    >
      FREEDOM
    </p>

    <div class="relative z-10 flex min-h-[100svh] flex-col justify-end px-6 pb-14 pt-28 md:px-12 md:pb-20 lg:px-16">
      <div class="mx-auto w-full max-w-7xl">
        <h2
          data-section-title
          class="max-w-5xl text-balance text-5xl font-black leading-[1.05] tracking-[-0.06em] text-white md:text-7xl lg:text-[6.5rem]"
        >
          我渴望自由，
          <br />
          <em class="font-normal not-italic text-[#539dfd]">去环游世界</em>
        </h2>

        <p
          data-reveal
          class="mt-6 max-w-xl text-sm leading-7 text-white/70 md:text-base md:leading-8"
        >
          代码之外，还有辽阔的山海与未知的远方。我想用脚步丈量世界，用双眼收藏自由。
        </p>
      </div>

      <!-- 环游目的地跑马灯 -->
      <div
        data-reveal
        class="mx-auto mt-12 w-full max-w-7xl overflow-hidden border-y border-white/12 py-4 [mask-image:linear-gradient(90deg,transparent,#000_8%,#000_92%,transparent)] md:mt-16 md:py-5"
      >
        <div class="freedom-dest-track flex w-max items-center gap-8 md:gap-12">
          <span
            v-for="(name, index) in track"
            :key="`${name}-${index}`"
            class="flex shrink-0 items-center gap-8 text-sm font-semibold uppercase tracking-[0.28em] text-white/55 md:gap-12 md:text-base"
          >
            <span class="text-white/88">{{ name }}</span>
            <span aria-hidden="true" class="h-1.5 w-1.5 rounded-full bg-[#539dfd]" />
          </span>
        </div>
      </div>
    </div>
  </section>
</template>
