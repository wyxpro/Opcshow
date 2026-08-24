<script setup lang="ts">
/** 3D 动态背景（Three.js）：暖色粒子流 + 鼠标视差 + 触摸支持；遵循系统减弱动态偏好 */
import * as THREE from 'three'
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = withDefaults(defineProps<{ intensity?: number }>(), { intensity: 0.6 })
const wrap = ref<HTMLElement | null>(null)
let renderer: THREE.WebGLRenderer | null = null
let raf = 0
let cleanup: (() => void) | null = null

onMounted(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduced || !wrap.value) return
  const el = wrap.value
  const w = el.clientWidth, h = el.clientHeight

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 100)
  camera.position.z = 8

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
  renderer.setSize(w, h)
  el.appendChild(renderer.domElement)

  // 暖色粒子云
  const count = Math.floor(420 * props.intensity) + 120
  const geo = new THREE.BufferGeometry()
  const pos = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)
  const palette = [new THREE.Color('#E4572E'), new THREE.Color('#D9932C'), new THREE.Color('#3D7A5E'), new THREE.Color('#C9BFA9')]
  for (let i = 0; i < count; i++) {
    pos[i * 3] = (Math.random() - 0.5) * 22
    pos[i * 3 + 1] = (Math.random() - 0.5) * 12
    pos[i * 3 + 2] = (Math.random() - 0.5) * 8
    const c = palette[Math.floor(Math.random() * palette.length)]
    colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3))
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  const mat = new THREE.PointsMaterial({ size: 0.07, vertexColors: true, transparent: true, opacity: 0.75 })
  const points = new THREE.Points(geo, mat)
  scene.add(points)

  // 柔和线条网格
  const grid = new THREE.GridHelper(30, 30, 0xD9D2C2, 0xE7E1D3)
  grid.position.y = -4.2
  ;(grid.material as THREE.Material).transparent = true
  ;(grid.material as THREE.Material).opacity = 0.35
  scene.add(grid)

  let mx = 0, my = 0
  const onMove = (e: PointerEvent) => {
    const r = el.getBoundingClientRect()
    mx = ((e.clientX - r.left) / r.width - 0.5) * 2
    my = ((e.clientY - r.top) / r.height - 0.5) * 2
  }
  el.addEventListener('pointermove', onMove)

  const clock = new THREE.Clock()
  const tick = () => {
    const t = clock.getElapsedTime()
    points.rotation.y = t * 0.05
    points.rotation.x = Math.sin(t * 0.18) * 0.06
    camera.position.x += (mx * 0.8 - camera.position.x) * 0.04
    camera.position.y += (-my * 0.5 - camera.position.y) * 0.04
    camera.lookAt(0, 0, 0)
    renderer!.render(scene, camera)
    raf = requestAnimationFrame(tick)
  }
  tick()

  const ro = new ResizeObserver(() => {
    const w2 = el.clientWidth, h2 = el.clientHeight
    camera.aspect = w2 / h2
    camera.updateProjectionMatrix()
    renderer!.setSize(w2, h2)
  })
  ro.observe(el)

  cleanup = () => {
    cancelAnimationFrame(raf)
    ro.disconnect()
    el.removeEventListener('pointermove', onMove)
    geo.dispose(); mat.dispose(); renderer?.dispose()
    renderer?.domElement.remove()
  }
})

onBeforeUnmount(() => cleanup?.())
</script>

<template>
  <div ref="wrap" class="three-bg" aria-hidden="true"></div>
</template>

<style scoped>
.three-bg { position: absolute; inset: 0; overflow: hidden; pointer-events: auto; }
.three-bg :deep(canvas) { display: block; }
</style>
