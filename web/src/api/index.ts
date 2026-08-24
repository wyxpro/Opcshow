/**
 * Opcshow API 封装层
 * 统一前缀 /api（Vite 代理到 FastAPI :8000）
 * 约定：GET 查询 / POST 创建 / PUT 更新 / DELETE 删除；错误抛 { detail }
 */

const BASE = '/api'

export function token(): string {
  return localStorage.getItem('opc_token') || ''
}
export function setToken(t: string) {
  t ? localStorage.setItem('opc_token', t) : localStorage.removeItem('opc_token')
}
export function isAdmin(): boolean {
  return !!token()
}

async function req(path: string, options: RequestInit = {}): Promise<any> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token()) headers['Authorization'] = `Bearer ${token()}`
  const res = await fetch(BASE + path, { ...options, headers: { ...headers, ...(options.headers || {}) } })
  if (!res.ok) {
    let detail = `请求失败 (${res.status})`
    try { detail = (await res.json()).detail || detail } catch { /* ignore */ }
    const err: any = new Error(detail)
    err.status = res.status
    throw err
  }
  return res.json()
}

export const api = {
  get: (p: string) => req(p),
  post: (p: string, body?: any) => req(p, { method: 'POST', body: JSON.stringify(body ?? {}) }),
  put: (p: string, body?: any) => req(p, { method: 'PUT', body: JSON.stringify(body ?? {}) }),
  del: (p: string) => req(p, { method: 'DELETE' }),
}

/* ---------- 类型定义（与后端数据格式一一对应） ---------- */
export interface Profile {
  name: string; title: string; bio: string; location: string; motto: string
  email: string; avatar: string; tags: string[]; socials: Record<string, string>
}
export interface Skill { id: number; name: string; level: number; category: string }
export interface Project { id: number; title: string; description: string; cover: string; link: string; tags: string[]; featured: number }
export interface Interest { id: number; name: string; icon: string; description: string }
export interface LayoutItem { id: string; title: string; span: number }
export interface KbCategory { id: number; name: string; parent_id: number; level: number; article_count: number; children: KbCategory[] }
export interface KbArticle { id: number; category_id: number; title: string; summary: string; content: string; tags: string[]; views: number; created_at: string; updated_at: string }
export interface Moment { id: number; content: string; images: string[]; location: string; mood: string; likes: number; created_at: string }
export interface TravelPoint { id: number; name: string; x: number; y: number; region: string; visit_date: string; note: string; photos: string[] }
export interface Music { id: number; title: string; artist: string; url: string; cover: string; liked: number }
export interface Movie { id: number; title: string; category: string; rating: number; year: number; poster: string; comment: string; status: string; director: string }
export interface Message { id: number; nickname: string; content: string; color: string; likes: number; pinned: number; reply: string; status: string; created_at: string }
export interface TimelineItem { id: number; event_date: string; title: string; description: string; tag: string }
export interface FriendLink { id: number; name: string; url: string; avatar: string; description: string; status: string }

export function fmtDate(s?: string): string {
  if (!s) return ''
  return s.slice(0, 10)
}
export function fromNow(s?: string): string {
  if (!s) return ''
  const diff = Date.now() - new Date(s.replace(' ', 'T')).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m} 分钟前`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h} 小时前`
  const d = Math.floor(h / 24)
  if (d < 30) return `${d} 天前`
  return fmtDate(s)
}
