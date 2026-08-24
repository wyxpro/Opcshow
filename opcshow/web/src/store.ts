/** 轻量全局状态（替代 Pinia，零依赖）：站点设置 + Toast 通知 */
import { reactive } from 'vue'
import { api } from './api'

export interface Toast { id: number; text: string; kind: 'ok' | 'warn' | '' }

export const store = reactive({
  settings: {
    site: { name: 'Opcshow', subtitle: '' },
    effects: { three: true, intensity: 0.6, style: 'particles' },
    theme: { accent: '#E4572E' },
    carousel: { interval: 4 },
    ai: { enabled: true, welcome: '' },
  } as any,
  toasts: [] as Toast[],
  loaded: false,
})

let toastId = 0
export function toast(text: string, kind: Toast['kind'] = '') {
  const id = ++toastId
  store.toasts.push({ id, text, kind })
  setTimeout(() => {
    const i = store.toasts.findIndex(t => t.id === id)
    if (i > -1) store.toasts.splice(i, 1)
  }, 2600)
}

export async function loadSettings() {
  if (store.loaded) return
  try {
    const data = await api.get('/settings')
    Object.assign(store.settings, data)
    store.loaded = true
    applyAccent()
  } catch { /* 服务未启动时静默 */ }
}

export function applyAccent() {
  const accent = store.settings?.theme?.accent
  if (accent) document.documentElement.style.setProperty('--accent', accent)
}
