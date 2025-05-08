import { createRouter, createWebHistory } from 'vue-router'

// 定义路由
const routes = [
  // 不需要导航栏的路由
  {
    path: '/login',
    name: 'LoginView',
    component: () => import('../views/LoginView.vue'),
    meta: { 
      hideHeader: true, // 标记不需要显示导航栏
      guest: true       // 标记为访客页面（已登录用户不应访问）
    }
  },
  // {
  //   path: '/register',
  //   name: 'RegisterView',
  //   component: () => import('../views/RegisterView.vue'),
  //   meta: { 
  //     hideHeader: true,
  //     guest: true
  //   }
  // },
  
  // 需要登录权限的路由
  {
    path: '/',
    name: 'HomeView',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/problems',
    name: 'ProblemsView',
    component: () => import('../views/ProblemsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/solutions',
    name: 'SolutionsView',
    component: () => import('../views/SolutionsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/solutions/trash',
    name: 'SolutionTrashView',
    component: () => import('../views/SolutionTrashView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/drafts/trash',
    name: 'DraftTrashView',
    component: () => import('../views/DraftTrashView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/drafts',
    name: 'DraftsView',
    component: () => import('../views/DraftsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/create',
    name: 'Create',
    component: () => import('@/views/CreateView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/create/solution',
    name: 'CreateSolution',
    component: () => import('@/views/CreateSolutionView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/create/question',
    name: 'CreateQuestion',
    component: () => import('@/views/CreateQuestionView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/questions/update/:id?',
    name: 'QuestionUpdate',
    component: () => import('@/views/QuestionUpdate.vue'),
    meta: { requiresAuth: true }
  },
  {
    path:'/trash',
    name: 'Trash',
    component: () => import('@/views/TrashView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path:'/problems/trash',
    name: 'ProblemsTrash',
    component: () => import('@/views/ProblemTrashView.vue'),
    meta: { requiresAuth: true }
  },
  
  // 详情页面也需要验证
  {
    path: '/:id/problems',
    name: 'QuestionDetail',
    component: () => import('@/views/QuestionDetailView.vue'),
    meta: { requiresAuth: true }
  },
  { 
    path: '/:id/solutions',
    name: 'SolutionDetail',
    component: () => import('@/views/SolutionDetailView.vue'),
    meta: { requiresAuth: true }
  },
  { 
    path: '/:id/drafts',
    name: 'DraftDetail',
    component: () => import('@/views/DraftDetailView.vue'),
    meta: { requiresAuth: true }
  },
  { 
    path: '/:id/solutions/update',
    name: 'Solution/update',
    component: () => import('@/views/SolutionUpdateView.vue'),
    meta: { requiresAuth: true }
  },
  { 
    path: '/:id/drafts/update',
    name: 'Draft/update',
    component: () => import('@/views/DraftUpdateView.vue'),
    meta: { requiresAuth: true }
  },
  
  // 404页面
  {
    path: '/:catchAll(.*)',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { 
      hideHeader: true  // 确保404页面不显示导航栏
    }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 强化路由守卫
router.beforeEach((to, from, next) => {
  console.log('路由切换:', to.path) // 调试日志
  
  const token = localStorage.getItem('access_token')
  
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth) && !token) {
    console.log('需要登录权限，重定向到登录页')
    // 保存原来要访问的页面路径，登录后可以重定向回去
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } 
  // 如果是访客页面（登录页）且用户已登录，重定向到首页
  else if (to.matched.some(record => record.meta.guest) && token) {
    console.log('已登录用户访问登录页，重定向到首页')
    next({ path: '/' })
  } 
  // 其他情况正常通过
  else {
    next()
  }
})

export default router