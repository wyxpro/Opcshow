/** ECharts 组合式函数：自动初始化 / 响应式 resize / 销毁 */
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, watch, type Ref } from 'vue'

export function useChart(el: Ref<HTMLElement | null>, getOption: () => echarts.EChartsOption) {
  let chart: echarts.ECharts | null = null
  let ro: ResizeObserver | null = null

  function render() {
    if (!el.value) return
    if (!chart) chart = echarts.init(el.value)
    chart.setOption(getOption(), true)
  }

  onMounted(() => {
    render()
    ro = new ResizeObserver(() => chart?.resize())
    if (el.value) ro.observe(el.value)
  })
  watch(getOption, () => render(), { deep: true })
  onBeforeUnmount(() => {
    ro?.disconnect()
    chart?.dispose()
    chart = null
  })
  return { refresh: render }
}
