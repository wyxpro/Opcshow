<script setup lang="ts">
/** 站长登录（演示账号 admin / admin123） */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, setToken } from '../api'
import { toast } from '../store'

const router = useRouter()
const route = useRoute()
const username = ref('admin')
const password = ref('')
const loading = ref(false)

async function login() {
  loading.value = true
  try {
    const res = await api.post('/auth/login', { username: username.value, password: password.value })
    setToken(res.token)
    toast(`欢迎回来，${res.user.nickname}`, 'ok')
    router.push((route.query.redirect as string) || '/admin')
  } catch (e: any) {
    toast(e.message, 'warn')
  } finally { loading.value = false }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card card">
      <div class="l-brand"><i></i><strong>Opcshow</strong></div>
      <h1>站长登录</h1>
      <p class="l-sub">登录后可编辑主页、管理内容、进入后台</p>
      <div class="field"><label>账号</label><input v-model="username" class="input" @keyup.enter="login" /></div>
      <div class="field"><label>密码</label><input v-model="password" type="password" class="input" placeholder="演示密码 admin123" @keyup.enter="login" /></div>
      <button class="btn btn-primary" style="width:100%" :disabled="loading" @click="login">
        {{ loading ? '登录中…' : '登 录' }}
      </button>
      <button class="back" @click="router.push('/')">← 返回主页看看</button>
    </div>
    <div class="l-deco d1"></div>
    <div class="l-deco d2"></div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(140deg, #F6F4EE, #EFE9DB); position: relative; overflow: hidden; padding: 20px;
}
.login-card { width: 380px; padding: 36px; position: relative; z-index: 2; animation: popIn .5s var(--ease-spring); }
.l-brand { display: flex; align-items: center; gap: 10px; margin-bottom: 22px; }
.l-brand i { width: 34px; height: 34px; border-radius: 11px; background: var(--accent); position: relative; }
.l-brand i::after { content: ''; position: absolute; inset: 9px; border: 3px solid #FFF5EC; border-radius: 50%; }
.l-brand strong { font-size: 17px; }
.login-card h1 { font-size: 22px; }
.l-sub { color: var(--muted); font-size: 13px; margin: 6px 0 20px; }
.back { display: block; margin: 16px auto 0; font-size: 13px; color: var(--muted); transition: color .2s; }
.back:hover { color: var(--accent); }
.l-deco { position: absolute; border-radius: 50%; filter: blur(2px); opacity: .5; }
.d1 { width: 340px; height: 340px; background: radial-gradient(circle, rgba(228,87,46,.25), transparent 70%); top: -80px; right: -60px; }
.d2 { width: 300px; height: 300px; background: radial-gradient(circle, rgba(61,122,94,.22), transparent 70%); bottom: -70px; left: -50px; }
</style>
