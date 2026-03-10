import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";

const routes = [
  {
    path: "/",
    component: () => import("../layouts/DefaultLayout.vue"),
    children: [
      {
        path: "",
        name: "Home",
        component: () => import("../views/HomeView.vue"),
      },
      {
        path: "products",
        name: "Products",
        component: () => import("../views/ProductListView.vue"),
      },
      {
        path: "products/:id",
        name: "ProductDetail",
        component: () => import("../views/ProductDetailView.vue"),
        props: true,
      },
      {
        path: "profile",
        name: "Profile",
        component: () => import("../views/ProfileView.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
  {
    path: "/auth",
    component: () => import("../layouts/AuthLayout.vue"),
    children: [
      {
        path: "login",
        name: "Login",
        component: () => import("../views/LoginView.vue"),
      },
      {
        path: "register",
        name: "Register",
        component: () => import("../views/RegisterView.vue"),
      },
    ],
  },
  {
    path: "/admin",
    component: () => import("../layouts/AdminLayout.vue"),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: "",
        name: "AdminDashboard",
        component: () => import("../views/admin/DashboardView.vue"),
      },
      {
        path: "products",
        name: "AdminProducts",
        component: () => import("../views/admin/ProductsView.vue"),
      },
    ],
  },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});

// 路由守卫
router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: "Login", query: { redirect: to.fullPath } };
  }
  if (to.meta.requiresAdmin && !auth.hasAdminAccess) {
    return { name: "Home" };
  }
  // 如果商家访问 dashboard，重定向到商品管理
  if (to.name === "AdminDashboard" && auth.isMerchant) {
    return { name: "AdminProducts" };
  }
});

export default router;
