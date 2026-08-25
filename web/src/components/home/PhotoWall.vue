<script setup lang="ts">
import { ref, computed } from 'vue'
import PhotoPreview, { type PhotoItem } from './PhotoPreview.vue'

export interface AlbumPhoto {
  id: number | string
  url: string
  original_url?: string
  description?: string
}

const props = defineProps<{
  photos?: AlbumPhoto[]
}>()

const DEFAULT_PHOTOS: AlbumPhoto[] = [
  { id: 1, url: 'https://bu.dusays.com/2025/08/09/689624f3698af.jpg', description: '雪山与未知的远方' },
  { id: 2, url: 'https://bu.dusays.com/2025/08/09/6896247e7aaf6.jpg', description: '代码与夜晚' },
  { id: 3, url: 'https://bu.dusays.com/2025/08/09/689623fe118af.jpg', description: '城市落日霞光' },
  { id: 4, url: 'https://bu.dusays.com/2025/08/09/6896246086c01.jpg', description: '海浪与微风' },
  { id: 5, url: 'https://bu.dusays.com/2025/08/09/689624cac990f.jpg', description: '森林里的晨光' },
  { id: 6, url: 'https://bu.dusays.com/2025/08/09/6896247f92f1f.jpg', description: '极光夜空' },
  { id: 7, url: 'https://bu.dusays.com/2025/08/09/689624d0475a5.jpg', description: '路过的海岸线' },
  { id: 8, url: 'https://bu.dusays.com/2025/08/09/6896240e1153a.jpg', description: '山谷星空' },
  { id: 9, url: 'https://bu.dusays.com/2025/08/09/689624f3698af.jpg', description: '远行笔记' },
  { id: 10, url: 'https://bu.dusays.com/2025/08/09/6896247e7aaf6.jpg', description: '自由的风' },
  { id: 11, url: 'https://bu.dusays.com/2025/08/09/689623fe118af.jpg', description: '街角光影' },
  { id: 12, url: 'https://bu.dusays.com/2025/08/09/6896246086c01.jpg', description: '记录当下' },
  { id: 13, url: 'https://bu.dusays.com/2025/08/09/689624cac990f.jpg', description: '时光剪影' },
  { id: 14, url: 'https://bu.dusays.com/2025/08/09/6896247f92f1f.jpg', description: '向往的山海' },
]

const previewOpen = ref(false)
const previewIndex = ref(0)

const activePhotos = computed(() => (props.photos && props.photos.length > 0 ? props.photos : DEFAULT_PHOTOS))

const previewPhotos = computed<PhotoItem[]>(() =>
  activePhotos.value.map((p) => ({
    id: String(p.id),
    url: p.original_url || p.url,
    alt: p.description || '相册照片',
  }))
)

interface Slot {
  top: string
  left: string
  width: number
  rotate: number
  z: number
  delay: number
  bob: number
  featured?: boolean
}

const SLOTS: Slot[] = [
  { top: '4%', left: '-2%', width: 300, rotate: -18, z: 4, delay: 0.1, bob: 5.2 },
  { top: '2%', left: '18%', width: 460, rotate: 7, z: 8, delay: 0.4, bob: 6.4, featured: true },
  { top: '6%', left: '48%', width: 280, rotate: -9, z: 5, delay: 0.8, bob: 4.8 },
  { top: '1%', left: '68%', width: 380, rotate: 14, z: 7, delay: 0.2, bob: 5.8 },
  { top: '8%', left: '88%', width: 260, rotate: -22, z: 3, delay: 1.1, bob: 4.4 },
  { top: '34%', left: '4%', width: 340, rotate: 11, z: 6, delay: 0.6, bob: 5.6 },
  { top: '38%', left: '28%', width: 240, rotate: -15, z: 4, delay: 1.3, bob: 4.2 },
  { top: '32%', left: '42%', width: 520, rotate: 3, z: 10, delay: 0.3, bob: 7.2, featured: true },
  { top: '36%', left: '72%', width: 320, rotate: -12, z: 6, delay: 0.9, bob: 5.4 },
  { top: '58%', left: '-4%', width: 360, rotate: 16, z: 5, delay: 0.5, bob: 6.0 },
  { top: '62%', left: '22%', width: 280, rotate: -8, z: 7, delay: 1.0, bob: 4.6 },
  { top: '56%', left: '46%', width: 400, rotate: 19, z: 8, delay: 0.15, bob: 6.8 },
  { top: '64%', left: '70%', width: 300, rotate: -16, z: 5, delay: 0.7, bob: 5.0 },
  { top: '58%', left: '90%', width: 270, rotate: 8, z: 4, delay: 1.2, bob: 4.9 },
]

const MARQUEE_TILTS = [-11, 4, -7] as const

const collage = computed(() => activePhotos.value.slice(0, SLOTS.length))

const marqueeRows = computed(() => {
  const photos = activePhotos.value
  const rows = [0, 1, 2].map((row) => photos.filter((_, i) => i % 3 === row))
  return rows.map((row) => {
    const base = row.length ? row : photos.slice(0, 4)
    const padded = [...base]
    while (padded.length < 6) padded.push(...base)
    return [...padded, ...padded]
  })
})

function openAt(index: number) {
  previewIndex.value = index
  previewOpen.value = true
}
</script>

<template>
  <section id="frames" data-section class="photo-wall relative min-h-[100svh] overflow-hidden py-20 md:py-0">
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_20%_20%,rgba(215,163,91,0.16),transparent_42%)]" />
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_85%_70%,rgba(159,232,208,0.12),transparent_46%)]" />
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_20%,rgba(5,6,8,0.55)_100%)]" />
    <div class="pointer-events-none absolute inset-x-0 top-0 z-[15] h-[42%] bg-[linear-gradient(180deg,rgba(5,6,8,0.92)_0%,rgba(5,6,8,0.55)_48%,transparent_100%)]" />

    <!-- 巨字水印 -->
    <p
      aria-hidden="true"
      class="photo-wall-watermark pointer-events-none absolute left-1/2 top-[42%] z-[1] -translate-x-1/2 -translate-y-1/2 select-none whitespace-nowrap font-black leading-none tracking-[-0.08em] text-white/[0.045]"
    >
      FRAMES
    </p>

    <!-- 主标题 -->
    <div class="photo-wall-copy relative z-30 mx-auto max-w-7xl px-6 md:absolute md:inset-x-0 md:top-10 md:px-12 lg:top-14 lg:px-16">
      <h2
        data-section-title
        class="photo-wall-headline mt-4 max-w-3xl text-balance text-4xl font-black leading-[1.08] tracking-[-0.06em] text-white md:text-6xl lg:text-7xl"
      >
        风景并不惊艳
        <br />
        <em class="font-normal not-italic text-[#e8b86a]">只是回忆加了分</em>
      </h2>
      <p data-reveal class="photo-wall-sub mt-4 max-w-md text-sm leading-7 text-white/80 md:text-base">
        记录那些按下快门的瞬间
      </p>
    </div>

    <!-- PC端：散落拼贴 -->
    <div data-reveal class="photo-wall-stage relative mx-auto hidden h-[110svh] max-w-[1600px] md:block">
      <button
        v-for="(photo, index) in collage"
        :key="photo.id"
        type="button"
        :class="['photo-wall-frame group absolute cursor-pointer border-0 bg-transparent p-0 text-left', SLOTS[index]?.featured ? 'photo-wall-frame--hero' : '']"
        :style="{
          top: SLOTS[index]?.top,
          left: SLOTS[index]?.left,
          width: `${SLOTS[index]?.width}px`,
          zIndex: SLOTS[index]?.z,
          '--pw-rotate': `${SLOTS[index]?.rotate}deg`,
          '--pw-delay': `${SLOTS[index]?.delay}s`,
          '--pw-bob': `${SLOTS[index]?.bob}s`,
        }"
        @click="openAt(index)"
      >
        <span class="photo-wall-lift block">
          <span class="photo-wall-bob block">
            <span class="photo-wall-polaroid relative block overflow-hidden rounded-[4px] bg-[#f3eee4] p-[10px] pb-9 shadow-[0_28px_80px_rgba(0,0,0,0.55)]">
              <span class="relative block aspect-[4/3] overflow-hidden bg-[#1a1b1f]">
                <img
                  :src="photo.url"
                  :alt="photo.description || `相册照片 ${index + 1}`"
                  class="h-full w-full object-cover"
                />
                <span class="pointer-events-none absolute inset-0 bg-[linear-gradient(145deg,rgba(255,255,255,0.12),transparent_40%,rgba(5,6,8,0.15))]" />
              </span>
              <span class="absolute bottom-2.5 left-3 right-3 flex items-center justify-between font-serif text-[10px] font-semibold uppercase tracking-[0.22em] text-[#2a241c]/70">
                <span>Frame {{ String(index + 1).padStart(2, '0') }}</span>
                <span class="text-[#c4923f]">●</span>
              </span>
            </span>
          </span>
        </span>
      </button>
    </div>

    <!-- 移动端：3行倾斜跑马灯 -->
    <div data-reveal class="relative mt-10 space-y-[-2.5rem] overflow-hidden py-8 [mask-image:linear-gradient(90deg,transparent,#000_5%,#000_95%,transparent)] md:hidden">
      <div
        v-for="(row, rowIndex) in marqueeRows"
        :key="`pw-row-${rowIndex}`"
        class="origin-center"
        :style="{ transform: `rotate(${MARQUEE_TILTS[rowIndex]}deg)` }"
      >
        <div
          :class="['photo-wall-marquee flex w-max gap-4', rowIndex % 2 ? 'photo-wall-marquee--reverse' : '']"
          :style="{ '--pw-marquee': `${28 + rowIndex * 6}s` }"
        >
          <button
            v-for="(photo, itemIndex) in row"
            :key="`${photo.id}-${rowIndex}-${itemIndex}`"
            type="button"
            class="photo-wall-polaroid relative h-[200px] w-[260px] shrink-0 cursor-pointer overflow-hidden rounded-[4px] border-0 bg-[#f3eee4] p-2 pb-7 shadow-[0_18px_50px_rgba(0,0,0,0.5)]"
            @click="openAt(Math.max(activePhotos.findIndex((p) => p.id === photo.id), 0))"
          >
            <span class="relative block h-full w-full overflow-hidden">
              <img :src="photo.url" alt="" class="h-full w-full object-cover" />
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- 底栏相册说明 -->
    <div class="relative z-20 mt-6 flex items-center justify-between px-4 md:absolute md:inset-x-0 md:bottom-10 md:mt-0 md:px-8">
      <p class="text-[11px] font-semibold uppercase tracking-[0.28em] text-white/35">
        Random · {{ activePhotos.length }} shots
      </p>
      <a
        href="https://frame.liuyuyang.net"
        target="_blank"
        rel="noreferrer"
        class="cursor-pointer text-[11px] font-semibold uppercase tracking-[0.28em] text-[#9fe8d0] hover:text-white transition-colors"
      >
        打开完整相册 →
      </a>
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
