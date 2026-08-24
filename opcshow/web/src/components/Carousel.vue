<script setup lang="ts">
/** 作品轮播：自动播放 + 触摸滑动 + 指示点 */
import { onBeforeUnmount, onMounted, ref } from 'vue'
import type { Project } from '../api'

const props = withDefaults(defineProps<{ items: Project[]; interval?: number }>(), { interval: 4 })
const idx = ref(0)
let timer: ReturnType<typeof setInterval> | null = null
const track = ref<HTMLElement | null>(null)

function go(i: number) {
  if (!props.items.length) return
  idx.value = ((i % props.items.length) + props.items.length) % props.items.length
}
function play() {
  stop()
  if (props.items.length > 1) timer = setInterval(() => go(idx.value + 1), props.interval * 1000)
}
function stop() { if (timer) clearInterval(timer); timer = null }

// 触摸滑动
let startX = 0
function onStart(e: PointerEvent) { startX = e.clientX; stop() }
function onEnd(e: PointerEvent) {
  const dx = e.clientX - startX
  if (Math.abs(dx) > 40) go(idx.value + (dx < 0 ? 1 : -1))
  play()
}

onMounted(play)
onBeforeUnmount(stop)
</script>

<template>
  <div class="carousel" @mouseenter="stop" @mouseleave="play">
    <div ref="track" class="track" :style="{ transform: `translateX(-${idx * 100}%)` }"
         @pointerdown="onStart" @pointerup="onEnd">
      <div v-for="p in items" :key="p.id" class="slide">
        <img :src="p.cover" :alt="p.title" loading="lazy" />
        <div class="slide-info">
          <strong>{{ p.title }}</strong>
          <p>{{ p.description }}</p>
          <div class="slide-tags">
            <span v-for="t in p.tags" :key="t" class="tag">{{ t }}</span>
          </div>
        </div>
      </div>
    </div>
    <button v-if="items.length > 1" class="arrow prev" @click="go(idx - 1)" aria-label="上一个">‹</button>
    <button v-if="items.length > 1" class="arrow next" @click="go(idx + 1)" aria-label="下一个">›</button>
    <div v-if="items.length > 1" class="dots">
      <i v-for="(p, i) in items" :key="p.id" :class="{ on: i === idx }" @click="go(i)"></i>
    </div>
  </div>
</template>

<style scoped>
.carousel { position: relative; border-radius: var(--radius); overflow: hidden; user-select: none; }
.track { display: flex; transition: transform .55s var(--ease); touch-action: pan-y; cursor: grab; }
.slide { flex: 0 0 100%; position: relative; aspect-ratio: 16/9; background: var(--bg-deep); }
.slide img { width: 100%; height: 100%; object-fit: cover; pointer-events: none; }
.slide-info {
  position: absolute; left: 0; right: 0; bottom: 0; padding: 40px 20px 16px;
  background: linear-gradient(transparent, rgba(24, 22, 18, .78));
  color: #F7F3EA;
}
.slide-info strong { font-size: 16px; display: block; }
.slide-info p { font-size: 12.5px; opacity: .82; margin: 3px 0 8px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
.slide-tags :deep(.tag) { background: rgba(255,255,255,.16); color: #F7F3EA; backdrop-filter: blur(4px); }
.arrow {
  position: absolute; top: 50%; transform: translateY(-50%);
  width: 34px; height: 34px; border-radius: 50%; font-size: 20px; line-height: 1;
  background: rgba(255,255,255,.85); color: var(--ink); opacity: 0; transition: opacity .25s;
  display: flex; align-items: center; justify-content: center;
}
.carousel:hover .arrow { opacity: 1; }
.prev { left: 12px } .next { right: 12px }
.dots { position: absolute; bottom: 12px; right: 16px; display: flex; gap: 6px; }
.dots i { width: 6px; height: 6px; border-radius: 99px; background: rgba(255,255,255,.5); cursor: pointer; transition: all .3s; }
.dots i.on { width: 18px; background: #fff; }
@media (max-width: 860px) { .arrow { display: none } }
</style>
