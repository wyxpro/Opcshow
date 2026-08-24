<script setup lang="ts">
/** 全屏弹幕引擎：轨道分配 + Web Animations 滚动 + 点赞 + 悬停暂停 */
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { api, type Message } from '../api'

const props = defineProps<{ messages: Message[] }>()
const wall = ref<HTMLElement | null>(null)
const anims: Animation[] = []
const TRACKS = 7

const colorOf = (m: Message) => m.color || '#E4572E'

async function spawn(m: Message) {
  if (!wall.value) return
  const el = document.createElement('div')
  el.className = 'dm-item'
  el.innerHTML = `<span class="dm-name" style="color:${colorOf(m)}">${escapeHtml(m.nickname)}：</span>${escapeHtml(m.content)}` +
    (m.pinned ? '<i class="dm-pin">置顶</i>' : '') +
    `<button class="dm-like">♥ ${m.likes || ''}</button>`
  el.style.borderColor = colorOf(m) + '33'
  const trackH = wall.value.clientHeight / TRACKS
  const track = Math.floor(Math.random() * TRACKS)
  el.style.top = `${track * trackH + 4}px`
  wall.value.appendChild(el)

  el.querySelector('.dm-like')?.addEventListener('click', async (e) => {
    e.stopPropagation()
    await api.post(`/social/messages/${m.id}/like`, {})
    const btn = el.querySelector('.dm-like')!
    btn.textContent = `♥ ${(m.likes || 0) + 1}`
    btn.classList.add('liked')
  }, { once: true })

  const width = el.offsetWidth
  const distance = wall.value.clientWidth + width
  const duration = 9000 + Math.random() * 7000
  const anim = el.animate(
    [{ transform: `translateX(${wall.value.clientWidth}px)` }, { transform: `translateX(-${width}px)` }],
    { duration, iterations: Infinity, easing: 'linear' }
  )
  el.addEventListener('mouseenter', () => anim.pause())
  el.addEventListener('mouseleave', () => anim.play())
  anims.push(anim)
  void distance
}

function escapeHtml(s: string) {
  return s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!))
}

function rebuild() {
  anims.forEach(a => a.cancel())
  anims.length = 0
  if (wall.value) wall.value.innerHTML = ''
  nextTick(() => props.messages.slice(0, 24).forEach((m, i) => setTimeout(() => spawn(m), i * 420)))
}

watch(() => props.messages, rebuild, { immediate: true, deep: true })
onBeforeUnmount(() => anims.forEach(a => a.cancel()))
</script>

<template>
  <div ref="wall" class="dm-wall"></div>
</template>

<style scoped>
.dm-wall {
  position: relative; height: 340px; overflow: hidden; border-radius: var(--radius);
  background:
    radial-gradient(600px 200px at 20% 0%, rgba(228, 87, 46, .06), transparent),
    radial-gradient(500px 200px at 90% 100%, rgba(61, 122, 94, .07), transparent),
    var(--surface);
  border: 1px solid var(--line-2);
}
:deep(.dm-item) {
  position: absolute; left: 0; display: inline-flex; align-items: center; gap: 6px;
  background: var(--surface-2); border: 1px solid var(--line-2);
  padding: 6px 14px; border-radius: 999px; font-size: 13.5px; white-space: nowrap;
  box-shadow: var(--shadow-sm); will-change: transform;
}
:deep(.dm-name) { font-weight: 600; }
:deep(.dm-pin) { font-size: 11px; background: var(--accent-soft); color: var(--accent-strong); padding: 1px 7px; border-radius: 6px; font-style: normal; }
:deep(.dm-like) { color: var(--muted); font-size: 12px; padding: 2px 6px; border-radius: 8px; transition: all .2s; }
:deep(.dm-like:hover), :deep(.dm-like.liked) { color: var(--rose); transform: scale(1.1); }
</style>
