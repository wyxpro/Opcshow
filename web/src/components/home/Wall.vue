<script setup lang="ts">
import { computed } from 'vue'

export interface WallItem {
  id: number | string
  name: string
  content: string
  color?: string
}

const props = defineProps<{
  walls?: WallItem[]
}>()

const DEFAULT_WALLS: WallItem[] = [
  { id: 1, name: '林一舟', content: '欢迎来到我的数字自留地！在这里记录技术与生活。', color: '#539dfd' },
  { id: 2, name: '访客小张', content: '首页的地球动效和拍立得墙好酷炫！支持！', color: '#9fe8d0' },
  { id: 3, name: '开源爱好者', content: 'ThriveX 项目很棒，一直在关注！加油！', color: '#d7a35b' },
  { id: 4, name: '前端同行', content: '全栈开发者的终极追寻，致敬热爱！', color: '#63d47f' },
  { id: 5, name: '路人甲', content: '界面设计太惊艳了，太有质感了。', color: '#f5efe6' },
  { id: 6, name: '星空极客', content: '坐标宁波，同在浙江，给大佬点赞！', color: '#b7d9ff' },
  { id: 7, name: '设计控', content: '配色和动画都很丝滑，UI/UX 细节拉满！', color: '#9fe8d0' },
  { id: 8, name: '全栈开发者', content: '热爱是所有的理由与解释，加油！', color: '#d7a35b' },
]

const wallTrackConfig = [
  { duration: 42, reverse: false },
  { duration: 50, reverse: true },
  { duration: 38, reverse: false },
  { duration: 46, reverse: true },
  { duration: 44, reverse: false },
  { duration: 52, reverse: true },
  { duration: 40, reverse: false },
] as const

const activeWalls = computed(() => (props.walls && props.walls.length > 0 ? props.walls : DEFAULT_WALLS))

const wallRows = computed(() => {
  const list = activeWalls.value
  return wallTrackConfig.map((_, rowIndex) =>
    list.filter((_, itemIndex) => itemIndex % wallTrackConfig.length === rowIndex)
  )
})

function padWallRow(row: WallItem[], minCount = 8) {
  if (!row.length) return []
  const padded = [...row]
  while (padded.length < minCount) padded.push(...row)
  return [...padded, ...padded]
}
</script>

<template>
  <section id="wall" data-section class="px-4 py-20 md:px-8 md:py-28">
    <div class="mx-auto mb-12 max-w-5xl text-center lg:mb-16">
      <h2 data-section-title class="mx-auto max-w-5xl text-balance text-4xl font-black leading-[1.1] tracking-[-0.06em] text-[#f5efe6] md:text-6xl lg:text-7xl">
        一些<em class="font-normal not-italic text-[#d7a35b]">留言</em>
      </h2>
    </div>

    <div data-reveal class="w-full py-5 md:py-6">
      <div
        v-if="activeWalls.length"
        class="relative h-[70vh] min-h-[560px] w-full overflow-hidden [mask-image:linear-gradient(90deg,transparent,#000_6%,#000_94%,transparent)]"
      >
        <div class="flex h-full w-full flex-col justify-between py-1">
          <div
            v-for="(row, rowIndex) in wallRows"
            :key="`wall-row-${rowIndex}`"
            class="overflow-hidden"
          >
            <div
              v-if="padWallRow(row).length"
              class="flex w-max items-stretch gap-3"
              :style="{
                animation: `marquee ${wallTrackConfig[rowIndex].duration}s linear infinite${wallTrackConfig[rowIndex].reverse ? ' reverse' : ''}`,
              }"
            >
              <article
                v-for="(wall, itemIndex) in padWallRow(row)"
                :key="`${wall.id}-${rowIndex}-${itemIndex}`"
                class="flex w-[min(300px,78vw)] shrink-0 items-start gap-2 px-1 py-1 text-sm md:w-[340px]"
              >
                <span class="shrink-0 text-xs font-semibold md:text-sm" :style="{ color: wall.color || '#9fe8d0' }">
                  {{ wall.name }}
                </span>
                <span class="shrink-0 text-white/25">：</span>
                <span class="line-clamp-3 min-w-0 flex-1 text-xs leading-relaxed text-white/70 md:text-sm">
                  {{ wall.content }}
                </span>
              </article>
            </div>
          </div>
        </div>
      </div>

      <article v-else data-reveal class="rounded-[24px] border border-white/10 bg-white/5 p-5 text-sm text-white/60">
        暂无留言数据
      </article>
    </div>
  </section>
</template>
