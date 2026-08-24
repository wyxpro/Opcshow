<script setup lang="ts">
/** 一键卡片式分享：Canvas 生成精美卡片 + 短链接复制 + 多渠道入口 */
import { ref } from 'vue'
import { api } from '../api'
import { toast } from '../store'

const props = defineProps<{ target: string; title?: string; desc?: string }>()
const emit = defineEmits<{ close: [] }>()

const info = ref<any>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const loading = ref(true)

async function build() {
  info.value = await api.get(`/social/share/${props.target}`)
  draw()
  loading.value = false
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + w, y, x + w, y + h, r)
  ctx.arcTo(x + w, y + h, x, y + h, r)
  ctx.arcTo(x, y + h, x, y, r)
  ctx.arcTo(x, y, x + w, y, r)
  ctx.closePath()
}

function draw() {
  const c = canvasRef.value!
  const ctx = c.getContext('2d')!
  const W = 640, H = 360
  // 纸感底
  ctx.fillStyle = '#F8F5EE'
  roundRect(ctx, 0, 0, W, H, 0); ctx.fill()
  // 装饰色块
  ctx.fillStyle = '#E4572E'
  ctx.beginPath(); ctx.arc(W - 40, 40, 130, 0, Math.PI * 2); ctx.fill()
  ctx.fillStyle = '#3D7A5E'
  ctx.beginPath(); ctx.arc(W - 90, 320, 90, 0, Math.PI * 2); ctx.globalAlpha = .85; ctx.fill(); ctx.globalAlpha = 1
  ctx.fillStyle = '#E8A13C'
  ctx.beginPath(); ctx.arc(60, 330, 46, 0, Math.PI * 2); ctx.fill()
  // Logo
  ctx.fillStyle = '#23262B'
  ctx.font = '600 26px "PingFang SC", sans-serif'
  ctx.fillText('◍ Opcshow', 40, 62)
  // 标题
  ctx.font = '700 34px "PingFang SC", sans-serif'
  ctx.fillStyle = '#23262B'
  ctx.fillText(info.value.title, 40, 150)
  // 描述
  ctx.font = '400 19px "PingFang SC", sans-serif'
  ctx.fillStyle = '#6B7078'
  ctx.fillText(info.value.desc, 40, 192)
  // 链接胶囊
  ctx.fillStyle = '#23262B'
  roundRect(ctx, 40, 232, 250, 46, 23); ctx.fill()
  ctx.fillStyle = '#F5F0E4'
  ctx.font = '500 17px monospace'
  ctx.fillText(info.value.url.replace('https://', ''), 62, 261)
  // 伪二维码
  ctx.fillStyle = '#23262B'
  const qx = W - 150, qy = 190, cell = 8
  for (let i = 0; i < 12; i++) for (let j = 0; j < 12; j++) {
    if ((i * 7 + j * 13 + i * j) % 3 === 0) ctx.fillRect(qx + i * cell, qy + j * cell, cell - 2, cell - 2)
  }
  ctx.font = '400 13px "PingFang SC", sans-serif'
  ctx.fillStyle = '#8C9099'
  ctx.fillText('扫码访问主页', qx + 4, qy + 12 * cell + 22)
}

function copyLink() {
  navigator.clipboard?.writeText(info.value.url)
    .then(() => toast('链接已复制，去粘贴分享吧', 'ok'))
    .catch(() => toast('复制失败', 'warn'))
}

function download() {
  const a = document.createElement('a')
  a.href = canvasRef.value!.toDataURL('image/png')
  a.download = `opcshow-share-${props.target}.png`
  a.click()
  toast('分享卡片已保存', 'ok')
}

function shareTo(channel: string) {
  const url = encodeURIComponent(info.value.url)
  const text = encodeURIComponent(info.value.title)
  const map: Record<string, string> = {
    weibo: `https://service.weibo.com/share/share.php?url=${url}&title=${text}`,
    qq: `https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${text}`,
  }
  if (channel === 'wechat') { toast('请保存卡片，在微信中分享', 'ok'); download(); return }
  window.open(map[channel], '_blank')
}

build()
</script>

<template>
  <div class="modal-mask" @click.self="emit('close')">
    <div class="modal share-modal">
      <div class="modal-head">
        <h3>分享 · 精美卡片</h3>
        <button class="icon-btn" @click="emit('close')">
          <svg viewBox="0 0 24 24" width="16" height="16"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="canvas-wrap"><canvas ref="canvasRef" width="640" height="360"></canvas></div>
        <div class="share-actions">
          <button class="btn btn-primary" @click="copyLink">复制短链接</button>
          <button class="btn btn-ghost" @click="download">保存卡片</button>
        </div>
        <div class="channels">
          <button @click="shareTo('wechat')"><i class="c-icon" style="background:#3D7A5E">微</i>微信</button>
          <button @click="shareTo('weibo')"><i class="c-icon" style="background:#D4572E">博</i>微博</button>
          <button @click="shareTo('qq')"><i class="c-icon" style="background:#2E86AB">Q</i>QQ</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.share-modal { max-width: 560px; }
.canvas-wrap { border-radius: 14px; overflow: hidden; border: 1px solid var(--line-2); box-shadow: var(--shadow); }
canvas { width: 100%; display: block; }
.share-actions { display: flex; gap: 10px; margin: 16px 0 12px; }
.channels { display: flex; gap: 18px; justify-content: center; padding-top: 10px; border-top: 1px dashed var(--line); }
.channels button { display: flex; flex-direction: column; align-items: center; gap: 5px; font-size: 12px; color: var(--ink-2); transition: transform .2s; }
.channels button:hover { transform: translateY(-2px); color: var(--ink); }
.c-icon { width: 38px; height: 38px; border-radius: 12px; color: #fff; display: flex; align-items: center; justify-content: center; font-style: normal; font-size: 15px; font-weight: 600; }
</style>
