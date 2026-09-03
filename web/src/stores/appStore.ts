/**
 * Pinia 规范化全局状态库 (含持久化插件)
 */
import { defineStore } from 'pinia'
import { api } from '../api'

export interface Toast { id: number; text: string; kind: 'ok' | 'warn' | '' }

export const useAppStore = defineStore('app', {
  state: () => ({
    settings: {
      site: { name: 'Opcshow', subtitle: '' },
      effects: { three: true, intensity: 0.6, style: 'particles' },
      theme: { accent: '#E4572E' },
      carousel: { interval: 4 },
      ai: { enabled: true, welcome: '' },
    } as any,
    toasts: [] as Toast[],
    loaded: false,
    token: localStorage.getItem('opc_token') || '',
  }),
  getters: {
    isAdmin: (state) => !!state.token,
  },
  actions: {
    setToken(t: string) {
      this.token = t
      if (t) localStorage.setItem('opc_token', t)
      else localStorage.removeItem('opc_token')
    },
    addToast(text: string, kind: Toast['kind'] = '') {
      const id = Date.now() + Math.random()
      this.toasts.push({ id, text, kind })
      setTimeout(() => {
        const index = this.toasts.findIndex((t) => t.id === id)
        if (index > -1) this.toasts.splice(index, 1)
      }, 2600)
    },
    async loadSettings() {
      if (this.loaded) return
      try {
        const data = await api.get('/settings')
        Object.assign(this.settings, data)
        this.loaded = true
        this.applyAccent()
      } catch {
        /* 静默处理 */
      }
    },
    applyAccent() {
      const accent = this.settings?.theme?.accent
      if (accent) document.documentElement.style.setProperty('--accent', accent)
    },
  },
  persist: true,
})
