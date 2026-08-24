<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import Hls from 'hls.js'

const videoRef = ref<HTMLVideoElement | null>(null)
const SRC = 'https://stream.mux.com/Aa02T7oM1wH5Mk5EEVDYhbZ1ChcdhRsS2m1NYyx4Ua1g.m3u8'
let hlsInstance: Hls | null = null

onMounted(() => {
  const video = videoRef.value
  if (!video) return

  if (Hls.isSupported()) {
    hlsInstance = new Hls()
    hlsInstance.loadSource(SRC)
    hlsInstance.attachMedia(video)
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = SRC
  }
})

onUnmounted(() => {
  if (hlsInstance) {
    hlsInstance.destroy()
    hlsInstance = null
  }
})
</script>

<template>
  <div class="pointer-events-none absolute inset-0 h-full w-full overflow-hidden">
    <video
      ref="videoRef"
      autoplay
      muted
      loop
      playsinline
      class="pointer-events-none absolute inset-0 h-full w-full object-cover"
    />
    <div class="pointer-events-none absolute inset-0 bg-black/60" />
  </div>
</template>
