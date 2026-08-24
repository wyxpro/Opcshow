<script setup lang="ts">
/**
 * 首页 · liuyuyang 品牌与个人动态主页 (Vue 3 端口与移动端响应式适配)
 */
import { ref, onMounted } from 'vue'
import { api } from '../api'

import Hero from '../components/home/Hero.vue'
import Location from '../components/home/Location.vue'
import Story from '../components/home/Story.vue'
import Freedom from '../components/home/Freedom.vue'
import PhotoWall from '../components/home/PhotoWall.vue'
import OpenSource from '../components/home/OpenSource.vue'
import Gallery from '../components/home/Gallery.vue'
import Sponsor from '../components/home/Sponsor.vue'
import Wall, { type WallItem } from '../components/home/Wall.vue'
import Quote from '../components/home/Quote.vue'
import Milestone, { type MilestoneItem } from '../components/home/Milestone.vue'

const walls = ref<WallItem[]>([])
const milestones = ref<MilestoneItem[]>([])

async function loadData() {
  try {
    const [messagesRes, timelineRes] = await Promise.allSettled([
      api.get('/messages'),
      api.get('/timeline')
    ])

    if (messagesRes.status === 'fulfilled' && Array.isArray(messagesRes.value)) {
      walls.value = messagesRes.value.map((msg: any) => ({
        id: msg.id,
        name: msg.author || msg.nickname || '访客',
        content: msg.content,
        color: msg.color || '#9fe8d0'
      }))
    }

    if (timelineRes.status === 'fulfilled' && Array.isArray(timelineRes.value)) {
      milestones.value = timelineRes.value.map((item: any) => ({
        id: item.id,
        eventDate: new Date(item.date || item.created_at || Date.now()).getTime(),
        title: item.title,
        description: item.content || item.description || '',
        image: item.image || item.cover,
        tags: item.tag ? [item.tag] : ['里程碑']
      }))
    }
  } catch (err) {
    console.warn('API 加载完成或使用默认备用数据', err)
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="home-page min-h-screen w-full overflow-x-hidden bg-[#050608] text-[#f4f0e8] selection:bg-[#b7ffe8] selection:text-[#050608]">
    <!-- 1. Hero 区域 (3D地球, 动态轨道标签, 个人状态) -->
    <Hero />

    <!-- 2. 地理位置 Location (宁波 OSM 地图, 坐标与定位动画) -->
    <Location />

    <!-- 3. 个人故事 Story (4步 GSAP 滚屏固定与段落切换) -->
    <Story />

    <!-- 4. 自由宣言 Freedom (背景视频, 环游世界跑马灯) -->
    <Freedom />

    <!-- 5. 拍立得照片墙 PhotoWall (散落卡片 & 移动端倾斜跑马灯) -->
    <PhotoWall />

    <!-- 6. 开源项目 OpenSource (视频背景 & 开源信仰) -->
    <OpenSource />

    <!-- 7. 作品画廊 Gallery (倾斜双轨道卡片 & Ken Burns 图片渐变) -->
    <Gallery />

    <!-- 8. 赞助商 Sponsor (独家赞助商 & 光辉闪耀效果) -->
    <Sponsor />

    <!-- 9. 留言弹幕墙 Wall (多轨道无缝跑马灯) -->
    <Wall :walls="walls" />

    <!-- 10. 登顶金句 Quote (高山视频背景 & GSAP 缩放 scrub 动效) -->
    <Quote />

    <!-- 11. 交互式里程碑 Milestone (SVG 正弦波浪, 星空背景, 拖拽时间轴) -->
    <Milestone :milestones="milestones" />
  </div>
</template>

<style scoped>
.home-page {
  font-family: 'Noto Serif SC', 'Songti SC', serif;
}
</style>
