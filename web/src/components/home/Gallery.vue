<script setup lang="ts">
const galleryImgs = [
  'https://bu.dusays.com/2025/08/09/689624f3698af.jpg',
  'https://bu.dusays.com/2025/08/09/6896247e7aaf6.jpg',
  'https://bu.dusays.com/2025/08/09/689623fe118af.jpg',
  'https://bu.dusays.com/2025/08/09/6896246086c01.jpg',
  'https://bu.dusays.com/2025/08/09/689624cac990f.jpg',
  'https://bu.dusays.com/2025/08/09/6896247f92f1f.jpg',
  'https://bu.dusays.com/2025/08/09/689624d0475a5.jpg',
  'https://bu.dusays.com/2025/08/09/6896240e1153a.jpg',
]

const topRow = [...galleryImgs, ...galleryImgs]
const bottomRow = [...galleryImgs].reverse().concat([...galleryImgs].reverse())
</script>

<template>
  <section id="studio" data-section class="relative overflow-hidden px-4 py-20 md:px-8 md:py-28">
    <div class="pointer-events-none absolute inset-x-0 top-1/3 h-[40%] bg-[radial-gradient(ellipse_at_center,rgba(159,232,208,0.1),transparent_68%)]" />

    <div class="mx-auto mb-12 grid max-w-7xl gap-6 lg:grid-cols-[0.8fr_1.2fr] lg:items-end">
      <div>
        <p data-section-title class="text-[11px] font-semibold uppercase tracking-[0.34em] text-[#9fe8d0]">
          Project
        </p>
        <h2 data-section-title class="mt-4 max-w-2xl text-4xl font-black leading-[1.12] tracking-[-0.06em] text-white md:text-6xl">
          这是我迄今为止投入<em class="font-normal not-italic text-[#9fe8d0]"> 时间和精力 </em>
          最多的<em class="font-normal not-italic text-[#d7a35b]"> 项目</em>。
        </h2>
      </div>
    </div>

    <div data-reveal class="gallery-stage relative overflow-hidden py-12 [mask-image:linear-gradient(90deg,transparent,#000_6%,#000_94%,transparent)] md:py-16">
      <!-- 顶层轨道 -->
      <div class="origin-center rotate-[-2.8deg]">
        <div class="gallery-track flex w-max gap-5 md:gap-7" style="--gallery-duration: 26s">
          <div
            v-for="(src, index) in topRow"
            :key="`${src}-${index}`"
            class="gallery-card-shell relative h-[240px] w-[340px] md:h-[300px] md:w-[440px]"
            :style="{
              '--gallery-delay': `${(index % 8) * 0.28}s`,
              '--gallery-bob': `${3.8 + (index % 5) * 0.45}s`,
              '--gallery-ken': `${10 + (index % 4) * 2.5}s`,
            }"
          >
            <div class="gallery-card group relative h-full w-full cursor-pointer overflow-hidden rounded-[28px] border border-white/12 bg-[#0a0c10] shadow-[0_24px_60px_rgba(0,0,0,0.45)]">
              <img
                :src="src"
                :alt="`ThriveX 界面 ${index + 1}`"
                class="object-cover object-center"
              />
              <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(5,6,8,0.02),rgba(5,6,8,0.42))]" />
              <div class="pointer-events-none absolute inset-0 opacity-0 ring-1 ring-inset ring-[#9fe8d0]/40 transition-opacity duration-300 group-hover:opacity-100" />
              <div class="pointer-events-none absolute bottom-0 left-0 right-0 translate-y-4 p-4 opacity-0 transition-[opacity,transform] duration-300 ease-out group-hover:translate-y-0 group-hover:opacity-100">
                <span class="text-[10px] font-bold uppercase tracking-[0.28em] text-[#9fe8d0]">
                  ThriveX · Shot {{ String((index % 8) + 1).padStart(2, '0') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底层反向轨道 -->
      <div class="mt-[-1.75rem] origin-center rotate-[2.4deg] md:mt-[-2.5rem]">
        <div class="gallery-track gallery-track-reverse flex w-max gap-5 md:gap-7" style="--gallery-duration: 34s">
          <div
            v-for="(src, index) in bottomRow"
            :key="`${src}-r-${index}`"
            class="gallery-card-shell relative h-[200px] w-[300px] md:h-[250px] md:w-[380px]"
            :style="{
              '--gallery-delay': `${(index % 8) * 0.28}s`,
              '--gallery-bob': `${3.8 + (index % 5) * 0.45}s`,
              '--gallery-ken': `${10 + (index % 4) * 2.5}s`,
            }"
          >
            <div class="gallery-card group relative h-full w-full cursor-pointer overflow-hidden rounded-[28px] border border-white/12 bg-[#0a0c10] shadow-[0_24px_60px_rgba(0,0,0,0.45)]">
              <img
                :src="src"
                :alt="`ThriveX 界面 ${index + 1}`"
                class="object-cover object-center"
              />
              <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,rgba(5,6,8,0.02),rgba(5,6,8,0.42))]" />
              <div class="pointer-events-none absolute inset-0 opacity-0 ring-1 ring-inset ring-[#9fe8d0]/40 transition-opacity duration-300 group-hover:opacity-100" />
              <div class="pointer-events-none absolute bottom-0 left-0 right-0 translate-y-4 p-4 opacity-0 transition-[opacity,transform] duration-300 ease-out group-hover:translate-y-0 group-hover:opacity-100">
                <span class="text-[10px] font-bold uppercase tracking-[0.28em] text-[#9fe8d0]">
                  ThriveX · Shot {{ String((index % 8) + 1).padStart(2, '0') }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
