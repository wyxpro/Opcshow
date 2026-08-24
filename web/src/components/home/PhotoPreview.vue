<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

export interface PhotoItem {
  id: string
  url: string
  thumb?: string
  alt?: string
}

const props = defineProps<{
  open: boolean
  photos: PhotoItem[]
  index?: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'change', newIndex: number): void
}>()

const rotation = ref(0)
const scale = ref(1)
const currentIndex = ref(props.index || 0)

watch(
  () => props.open,
  (val) => {
    if (val) {
      currentIndex.value = Math.min(Math.max(props.index || 0, 0), Math.max(props.photos.length - 1, 0))
      rotation.value = 0
      scale.value = 1
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
)

watch(
  () => props.index,
  (val) => {
    if (val !== undefined) {
      currentIndex.value = Math.min(Math.max(val, 0), Math.max(props.photos.length - 1, 0))
    }
  }
)

function setIndex(next: number) {
  if (!props.photos.length) return
  const normalized = (next + props.photos.length) % props.photos.length
  currentIndex.value = normalized
  rotation.value = 0
  scale.value = 1
  emit('change', normalized)
}

function goPrev() {
  if (props.photos.length <= 1) return
  setIndex(currentIndex.value - 1)
}

function goNext() {
  if (props.photos.length <= 1) return
  setIndex(currentIndex.value + 1)
}

function handleKeydown(e: KeyboardEvent) {
  if (!props.open) return
  if (e.key === 'Escape') emit('close')
  if (e.key === 'ArrowLeft') goPrev()
  if (e.key === 'ArrowRight') goNext()
}

function onWheel(e: WheelEvent) {
  e.preventDefault()
  if (e.deltaY < 0) {
    scale.value = Math.min(scale.value + 0.1, 3)
  } else {
    scale.value = Math.max(scale.value - 0.1, 0.4)
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open && photos.length"
      class="photo-preview-overlay fixed inset-0 z-[300] flex items-center justify-center bg-black/90 backdrop-blur-md"
      @click="emit('close')"
      role="dialog"
      aria-modal="true"
    >
      <!-- 关闭按钮 -->
      <button
        type="button"
        class="absolute right-5 top-5 z-10 inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-full border border-white/20 bg-white/10 text-white/80 transition-colors hover:bg-white/20 hover:text-white"
        @click="emit('close')"
        aria-label="关闭预览"
      >
        <svg viewBox="0 0 24 24" class="h-5 w-5 stroke-current fill-none stroke-2"><path d="M18 6L6 18M6 6l12 12" /></svg>
      </button>

      <!-- 上一张 -->
      <button
        v-if="photos.length > 1"
        type="button"
        class="absolute left-5 top-1/2 z-10 inline-flex h-12 w-12 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full border border-white/30 bg-neutral-800/50 text-white transition-colors hover:bg-neutral-800/80"
        @click.stop="goPrev"
        aria-label="上一张"
      >
        <svg viewBox="0 0 24 24" class="h-6 w-6 stroke-current fill-none stroke-2"><path d="M15 18l-6-6 6-6" /></svg>
      </button>

      <!-- 下一张 -->
      <button
        v-if="photos.length > 1"
        type="button"
        class="absolute right-5 top-1/2 z-10 inline-flex h-12 w-12 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full border border-white/30 bg-neutral-800/50 text-white transition-colors hover:bg-neutral-800/80"
        @click.stop="goNext"
        aria-label="下一张"
      >
        <svg viewBox="0 0 24 24" class="h-6 w-6 stroke-current fill-none stroke-2"><path d="M9 18l6-6-6-6" /></svg>
      </button>

      <!-- 图片显示区域 -->
      <div
        class="relative z-10 flex h-[min(760px,calc(100vh-130px))] w-[min(1040px,calc(100vw-96px))] items-center justify-center overflow-hidden"
        @wheel="onWheel"
        @click.stop
      >
        <img
          :src="photos[currentIndex]?.url"
          :alt="photos[currentIndex]?.alt || ''"
          class="h-full w-full select-none object-contain transition-transform duration-200 ease-out"
          :style="{ transform: `rotate(${rotation}deg) scale(${scale})` }"
          draggable="false"
        />
      </div>

      <!-- 控制工具栏 -->
      <div
        class="absolute bottom-7 left-1/2 z-20 flex -translate-x-1/2 items-center gap-2 rounded-full border border-white/20 bg-neutral-900/70 px-4 py-2 backdrop-blur-xl"
        @click.stop
      >
        <button
          v-if="photos.length > 1"
          type="button"
          class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/15 hover:text-white"
          @click="goPrev"
        >
          <svg viewBox="0 0 24 24" class="h-5 w-5 stroke-current fill-none stroke-2"><path d="M15 18l-6-6 6-6" /></svg>
        </button>

        <button
          type="button"
          class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/15 hover:text-white"
          @click="rotation -= 90"
          title="向左旋转"
        >
          <svg viewBox="0 0 24 24" class="h-4 w-4 stroke-current fill-none stroke-2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8M3 3v5h5" /></svg>
        </button>

        <button
          type="button"
          class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/15 hover:text-white"
          @click="rotation += 90"
          title="向右旋转"
        >
          <svg viewBox="0 0 24 24" class="h-4 w-4 stroke-current fill-none stroke-2"><path d="M21 12a9 9 0 1 1-9-9 9.75 9.75 0 0 1 6.74 2.74L21 8M21 3v5h-5" /></svg>
        </button>

        <button
          type="button"
          class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/15 hover:text-white"
          @click="scale = Math.max(scale - 0.2, 0.4)"
          title="缩小"
        >
          <svg viewBox="0 0 24 24" class="h-4 w-4 stroke-current fill-none stroke-2"><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35M8 11h6" /></svg>
        </button>

        <button
          type="button"
          class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/15 hover:text-white"
          @click="scale = Math.min(scale + 0.2, 3)"
          title="放大"
        >
          <svg viewBox="0 0 24 24" class="h-4 w-4 stroke-current fill-none stroke-2"><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35M11 8v6M8 11h6" /></svg>
        </button>

        <button
          v-if="photos.length > 1"
          type="button"
          class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/15 hover:text-white"
          @click="goNext"
        >
          <svg viewBox="0 0 24 24" class="h-5 w-5 stroke-current fill-none stroke-2"><path d="M9 18l6-6-6-6" /></svg>
        </button>

        <span v-if="photos.length > 1" class="ml-1 text-xs font-mono text-white/60">
          {{ currentIndex + 1 }} / {{ photos.length }}
        </span>
      </div>
    </div>
  </Teleport>
</template>
