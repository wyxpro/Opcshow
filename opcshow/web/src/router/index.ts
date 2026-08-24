import { createRouter, createWebHistory } from 'vue-router'
import { isAdmin } from '../api'

/**
 * 路由结构（与 PRD 五大菜单一一对应）
 * /            首页 · 个人总览
 * /work/*      工作 · 知识库(三级目录) + 在线简历
 * /life/*      生活 · 朋友圈/恋爱/旅拍/运动/游戏
 * /fun/*       娱乐 · 音乐盒/电影/百宝箱
 * /me/*        我的 · 友链/留言弹幕/时间轴/自媒体矩阵
 * /admin       后台管理（需登录）
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('../views/LoginView.vue'), meta: { title: '登录' } },
    {
      path: '/',
      component: () => import('../layout/MainLayout.vue'),
      children: [
        { path: '', name: 'home', component: () => import('../views/HomeView.vue'), meta: { title: '首页', group: 'home' } },
        { path: 'work/knowledge', name: 'knowledge', component: () => import('../views/work/KnowledgeView.vue'), meta: { title: '知识库', group: 'work' } },
        { path: 'work/article/:id', name: 'article', component: () => import('../views/work/ArticleView.vue'), meta: { title: '阅读', group: 'work' } },
        { path: 'work/resume', name: 'resume', component: () => import('../views/work/ResumeView.vue'), meta: { title: '在线简历', group: 'work' } },
        { path: 'life/moments', name: 'moments', component: () => import('../views/life/MomentsView.vue'), meta: { title: '朋友圈', group: 'life' } },
        { path: 'life/love', name: 'love', component: () => import('../views/life/LoveView.vue'), meta: { title: '恋爱记录', group: 'life' } },
        { path: 'life/travel', name: 'travel', component: () => import('../views/life/TravelView.vue'), meta: { title: '旅拍地图', group: 'life' } },
        { path: 'life/sports', name: 'sports', component: () => import('../views/life/SportsView.vue'), meta: { title: '运动数据', group: 'life' } },
        { path: 'life/games', name: 'games', component: () => import('../views/life/GamesView.vue'), meta: { title: '游戏档案', group: 'life' } },
        { path: 'fun/music', name: 'music', component: () => import('../views/fun/MusicView.vue'), meta: { title: '音乐盒', group: 'fun' } },
        { path: 'fun/movies', name: 'movies', component: () => import('../views/fun/MoviesView.vue'), meta: { title: '电影收藏', group: 'fun' } },
        { path: 'fun/box', name: 'box', component: () => import('../views/fun/BoxView.vue'), meta: { title: '百宝箱', group: 'fun' } },
        { path: 'me/links', name: 'links', component: () => import('../views/me/LinksView.vue'), meta: { title: '友情链接', group: 'me' } },
        { path: 'me/messages', name: 'messages', component: () => import('../views/me/MessagesView.vue'), meta: { title: '留言弹幕', group: 'me' } },
        { path: 'me/timeline', name: 'timeline', component: () => import('../views/me/TimelineView.vue'), meta: { title: '成长时间轴', group: 'me' } },
        { path: 'me/matrix', name: 'matrix', component: () => import('../views/me/MatrixView.vue'), meta: { title: '自媒体矩阵', group: 'me' } },
        { path: 'admin', name: 'admin', component: () => import('../views/AdminView.vue'), meta: { title: '后台管理', group: 'admin', requiresAuth: true } },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAdmin()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  document.title = to.meta.title ? `${to.meta.title} · Opcshow` : 'Opcshow'
})

export default router
