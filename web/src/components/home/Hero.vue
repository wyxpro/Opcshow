<script setup lang="ts">
import Earth from './Earth.vue'

const orbitTags = [
  { label: '🤖️ 数码科技爱好者', className: 'left-[2%] top-[8%] w-[42%]' },
  { label: '🔍 分享与热心帮助', className: 'right-[0%] top-[8%] w-[44%]' },
  { label: '💻 全栈开发工程师', className: 'left-[0%] top-[34%] w-[36%]' },
  { label: '源于热爱而发电 ✨', className: 'right-[4%] top-[34%] w-[34%]' },
  { label: '开源项目作者 🥳', className: 'left-[6%] bottom-[12%] w-[40%]' },
  { label: '热爱漫无边际 🎉', className: 'right-[4%] bottom-[12%] w-[34%]' },
] as const
</script>

<template>
  <section id="top" data-section class="relative min-h-screen overflow-hidden px-4 pb-10 pt-24 md:px-8 md:pb-16 md:pt-32">
    <Earth />

    <div class="relative z-10 mx-auto grid max-w-7xl items-start gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16">
      <div>
        <p data-hero-meta class="mb-5 text-[11px] font-semibold uppercase tracking-[0.34em] text-[#539dfd]">
          一个平凡的人
        </p>

        <div class="overflow-hidden">
          <h1 class="text-balance font-black tracking-[-0.06em] text-white">
            <span data-hero-word class="mb-4 flex items-center gap-3 text-[2rem] leading-none md:mb-5 md:text-5xl lg:text-[3.5rem]">
              <span aria-hidden="true" class="inline-block origin-bottom translate-y-0.5 text-[0.92em]">👋</span>
              <span>Hello,</span>
            </span>
            <span data-hero-word class="block text-5xl leading-[1.12] text-[#f5efe6] md:text-7xl lg:text-[6.75rem]">
              我叫
            </span>
            <span data-hero-word class="mt-1 block text-5xl leading-[1.08] text-[#539dfd] md:text-7xl lg:text-[7.25rem]">
              刘宇阳
            </span>
          </h1>
        </div>

        <div data-hero-meta class="mt-7 max-w-2xl space-y-5 text-sm leading-7 text-white/65 md:text-base md:leading-8">
          <p>
            我是一名02年的 <strong class="text-white font-medium">全栈工程师</strong>。
          </p>
          <p>
            一直对网站开发领域很感兴趣，<strong class="text-white font-medium">从小就希望有一个属于自己的网站</strong>，在17年时候成功进入站长圈，并通过各种自学，以及各种折腾，才有了你现在看到的这个网站
          </p>
        </div>

        <div data-hero-meta class="mt-9 flex flex-wrap gap-3">
          <a
            href="https://liuyuyang.net"
            target="_blank"
            rel="noreferrer"
            class="group inline-flex cursor-pointer items-center gap-2 rounded-full bg-[#539dfd] px-6 py-3.5 text-[11px] font-bold uppercase tracking-[0.22em] text-[#050608] shadow-[0_10px_30px_rgba(83,157,253,0.2)] transition-all duration-300 ease-out hover:-translate-y-1 hover:scale-[1.02] hover:shadow-[0_14px_34px_rgba(83,157,253,0.28)]"
          >
            个人博客
            <svg viewBox="0 0 24 24" class="h-4 w-4 fill-none stroke-current stroke-2 transition-transform duration-300 group-hover:scale-110"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15z" /></svg>
          </a>

          <a
            href="https://github.com/LiuYuYang01"
            target="_blank"
            rel="noreferrer"
            class="group inline-flex cursor-pointer items-center gap-2 rounded-full border border-white/12 bg-white/5 px-6 py-3.5 text-[11px] font-bold uppercase tracking-[0.22em] text-white/80 shadow-[0_10px_30px_rgba(0,0,0,0.16)] transition-all duration-300 ease-out hover:-translate-y-1 hover:scale-[1.02] hover:border-[#539dfd]/40 hover:bg-white/10 hover:text-white"
          >
            GitHub
            <svg viewBox="0 0 24 24" class="h-4 w-4 fill-current transition-transform duration-300 group-hover:rotate-12"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" /></svg>
          </a>
        </div>

        <div data-hero-meta class="mt-12 grid grid-cols-2 gap-3 text-[11px] uppercase tracking-[0.22em] text-white/45 sm:grid-cols-4">
          <div class="rounded-[18px] border border-white/10 bg-white/5 p-4">
            <span class="block text-white/65">角色</span>
            <strong class="mt-2 block text-sm tracking-normal text-white">前端 / 后端</strong>
          </div>
          <div class="rounded-[18px] border border-white/10 bg-white/5 p-4">
            <span class="block text-white/65">坐标</span>
            <strong class="mt-2 block text-sm tracking-normal text-white">浙江 · 宁波</strong>
          </div>
          <div class="rounded-[18px] border border-white/10 bg-white/5 p-4">
            <span class="block text-white/65">开源</span>
            <strong class="mt-2 block text-sm tracking-normal text-white">ThriveX</strong>
          </div>
          <div class="rounded-[18px] border border-white/10 bg-white/5 p-4">
            <span class="block text-white/65">态度</span>
            <strong class="mt-2 block text-sm tracking-normal text-white">热爱驱动</strong>
          </div>
        </div>
      </div>

      <div data-hero-visual class="relative mx-auto flex w-full max-w-[560px] items-center justify-center py-8 lg:py-10">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.03),transparent_62%)]" />
        <div class="relative flex h-[480px] w-full items-center justify-center md:h-[560px]">
          <!-- 头像中心 -->
          <div data-orbit-avatar class="absolute z-10 h-[220px] w-[220px] cursor-pointer overflow-hidden rounded-full border border-white/12 bg-[#0b0f14] p-2 shadow-[0_24px_70px_rgba(0,0,0,0.55)] transition-transform duration-500 ease-out hover:scale-[1.04] md:h-[250px] md:w-[250px]">
            <div class="relative h-full w-full overflow-hidden rounded-full bg-white/5">
              <img src="https://q.qlogo.cn/g?b=qq&nk=3311118881&s=640" alt="刘宇阳头像" class="h-full w-full object-cover object-center" />
            </div>
            <span class="absolute bottom-5 right-5 h-4 w-4 rounded-full border-4 border-[#0b0f14] bg-[#63d47f]" />
          </div>

          <!-- 环绕 3D 浮动标签 -->
          <div
            v-for="(tag, index) in orbitTags"
            :key="tag.label"
            data-orbit-tag
            :class="['absolute', tag.className, 'z-20 flex justify-center', index % 2 === 0 ? 'md:justify-start' : 'md:justify-end']"
            :style="{ animationDelay: `${index * 0.35}s` }"
          >
            <span class="orbit-tag-float inline-flex max-w-full cursor-pointer items-center rounded-full border border-white/12 bg-[#20252f]/90 px-4 py-2 text-[11px] font-medium leading-5 text-white/85 shadow-[0_12px_40px_rgba(0,0,0,0.22)] backdrop-blur-md transition-transform duration-500 ease-out hover:scale-[1.06]">
              {{ tag.label }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
