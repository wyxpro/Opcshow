<script setup lang="ts">
/** 模块内子导航：胶囊式 Tab，横向滚动适配移动端 */
import { useRoute, useRouter } from 'vue-router'

defineProps<{ items: { name: string; path: string }[] }>()
const route = useRoute()
const router = useRouter()
</script>

<template>
  <div class="sec-tabs">
    <a v-for="it in items" :key="it.path" :class="{ on: route.path === it.path }" @click="router.push(it.path)">
      {{ it.name }}
    </a>
  </div>
</template>

<style scoped>
.sec-tabs {
  display: flex; gap: 4px; margin-bottom: 20px; padding: 4px;
  background: var(--surface); border: 1px solid var(--line-2); border-radius: 999px;
  width: fit-content; max-width: 100%; overflow-x: auto; box-shadow: var(--shadow-sm);
}
.sec-tabs a {
  padding: 7px 18px; border-radius: 999px; font-size: 13.5px; color: var(--ink-2);
  cursor: pointer; white-space: nowrap; transition: all .25s var(--ease);
}
.sec-tabs a:hover { color: var(--ink); }
.sec-tabs a.on { background: var(--ink); color: #F5F2EA; font-weight: 500; box-shadow: 0 4px 10px -4px rgba(35,38,43,.4); }
</style>
