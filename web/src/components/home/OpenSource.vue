<script setup lang="ts">
const VIDEO_SRC =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260613_180732_a54afbf6-b30d-470e-861f-669871f09f67.mp4'
</script>

<template>
  <section id="open-source" data-section class="relative min-h-[100svh] overflow-hidden">
    <div data-parallax class="absolute inset-[-8%] will-change-transform">
      <video
        :src="VIDEO_SRC"
        autoplay
        muted
        loop
        playsinline
        preload="metadata"
        aria-label="开源创作氛围"
        class="opensource-video h-full w-full object-cover"
      />
    </div>

    <!-- 遮罩面板 -->
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(5,6,8,0.72)_0%,rgba(5,6,8,0.28)_36%,rgba(5,6,8,0.62)_72%,rgba(5,6,8,0.96)_100%)]" />
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_24%,rgba(5,6,8,0.68)_100%)]" />
    <div class="pointer-events-none absolute -left-1/4 top-0 h-[55%] w-[70%] bg-[radial-gradient(ellipse_at_center,rgba(159,232,208,0.2),transparent_65%)]" />
    <div class="pointer-events-none absolute -right-1/5 bottom-1/5 h-[48%] w-[55%] bg-[radial-gradient(ellipse_at_center,rgba(215,163,91,0.14),transparent_68%)]" />

    <div class="relative z-10 flex min-h-[100svh] flex-col justify-start px-10 pb-10 pt-[38.2svh] md:px-20 md:pb-14 lg:px-28 xl:px-36">
      <div class="mx-auto w-full max-w-[1360px]">
        <h2
          data-section-title
          class="max-w-5xl text-balance text-5xl font-black leading-[1.05] tracking-[-0.06em] text-white md:text-7xl lg:text-[6.5rem]"
        >
          对了，我还有一个
          <em class="font-normal not-italic text-[#d7a35b]">身份</em>
          <br />
          我是一名
          <em class="font-normal not-italic text-[#9fe8d0]">开源项目作者</em>
        </h2>

        <p
          data-reveal
          class="mt-6 max-w-xl text-sm leading-7 text-white/70 md:text-base md:leading-8"
        >
          热爱是所有的理由与解释
        </p>
      </div>
    </div>
  </section>
</template>
