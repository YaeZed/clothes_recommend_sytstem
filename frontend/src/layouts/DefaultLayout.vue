<template>
  <div class="layout">
    <!-- 淘宝风格顶部导航 (Site Nav) -->
    <div class="site-nav">
      <div class="container flex-between">
        <!-- 左侧 -->
        <div class="nav-left">
          <span class="welcome-text">欢迎来到穿搭推荐！</span>
          <template v-if="auth.isLoggedIn">
            <span class="user-greeting">Hi, {{ auth.user?.username }}</span>
            <a
              @click.prevent="showLogoutDialog = true"
              href="#"
              class="logout-link"
              >退出</a
            >
          </template>
          <template v-else>
            <router-link to="/auth/login" class="login-link text-primary"
              >亲，请登录</router-link
            >
            <router-link to="/auth/register">免费注册</router-link>
          </template>
        </div>
        <!-- 右侧 -->
        <div class="nav-right">
          <router-link to="/">首页</router-link>
          <span class="divider"></span>

          <el-dropdown v-if="auth.isLoggedIn" trigger="hover">
            <span class="nav-link el-dropdown-link"
              >我的穿搭 <el-icon><ArrowDown /></el-icon
            ></span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/profile')"
                  >个人中心</el-dropdown-item
                >
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <span class="divider" v-if="auth.isLoggedIn"></span>

          <div
            class="nav-link cart-link"
            @click="showCart = true"
            v-if="auth.isLoggedIn"
          >
            <el-icon><ShoppingCart /></el-icon> 购物车
            <strong class="text-primary fw-700" v-if="cart.totalCount">{{
              cart.totalCount
            }}</strong>
          </div>

          <span class="divider" v-if="auth.isLoggedIn"></span>

          <router-link
            to="/profile?tab=favorites"
            class="nav-link"
            v-if="auth.isLoggedIn"
          >
            <el-icon><Star /></el-icon> 收藏夹
          </router-link>

          <span class="divider" v-if="auth.isAdmin"></span>
          <router-link v-if="auth.isAdmin" to="/admin"
            >卖家中心(后台)</router-link
          >
        </div>
      </div>
    </div>

    <!-- 淘宝主头部 -->
    <header class="main-header">
      <div class="container header-inner">
        <!-- Logo -->
        <router-link to="/" class="logo">
          <span class="logo-icon">👗</span>
          <div class="logo-text">
            <span class="logo-main text-primary">穿搭推荐</span>
            <span class="logo-sub">精准匹配最美穿搭</span>
          </div>
        </router-link>

        <!-- 大搜索框 -->
        <div class="search-wrap">
          <div class="tb-search">
            <input
              v-model="keyword"
              @keyup.enter="doSearch"
              placeholder="搜索连衣裙、T恤、外套..."
              class="tb-search-input"
            />
            <button @click="doSearch" class="tb-search-btn">搜 索</button>
          </div>
          <!-- 热门搜索 -->
          <div class="hot-keywords">
            <span
              v-for="kw in hotKws"
              :key="kw"
              @click="quickSearch(kw)"
              class="kw-tag"
              >{{ kw }}</span
            >......
          </div>
        </div>
      </div>
    </header>

    <!-- 购物车抽屉 -->
    <CartDrawer :visible="showCart" @close="showCart = false" />

    <!-- 退出确认框 -->
    <el-dialog
      v-model="showLogoutDialog"
      title="退出登录"
      width="360px"
      align-center
    >
      <div
        style="
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          padding: 16px 0;
        "
      >
        <el-icon size="52" color="#ff5000"><WarningFilled /></el-icon>
        <p style="font-size: 15px; color: #333">确定要退出登录吗？</p>
      </div>
      <template #footer>
        <div
          style="display: flex; justify-content: center; gap: 12px; width: 100%"
        >
          <el-button @click="showLogoutDialog = false" style="width: 100px"
            >取消</el-button
          >
          <el-button type="primary" @click="confirmLogout" style="width: 100px"
            >确认退出</el-button
          >
        </div>
      </template>
    </el-dialog>

    <!-- 分类导航 -->
    <nav class="category-nav">
      <div class="container">
        <div class="cat-list">
          <router-link
            to="/"
            class="cat-item"
            :class="{ active: $route.path === '/' }"
          >
            🏠 首页
          </router-link>
          <router-link
            v-for="cat in categories"
            :key="cat"
            :to="`/products?category=${cat}`"
            class="cat-item"
            :class="{ active: $route.query.category === cat }"
            >{{ cat }}</router-link
          >
          <router-link
            to="/products"
            class="cat-item"
            :class="{
              active: $route.path === '/products' && !$route.query.category,
            }"
          >
            全部商品
          </router-link>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="container">
        <router-view />
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p>© 2026 穿搭推荐系统--基于 CF/SVD/DeepFM 混合推荐算法</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../store/auth";
import { ElMessage } from "element-plus";
import {
  Search,
  User,
  Star,
  UserFilled,
  SwitchButton,
  WarningFilled,
  ShoppingCart,
} from "@element-plus/icons-vue";
import { getCategories } from "../api/product";
import { useFavStore } from "../store/favorites";
import { useCartStore } from "../store/cart";
import CartDrawer from "../components/CartDrawer.vue";

const auth = useAuthStore();
const favs = useFavStore();
const cart = useCartStore();
const router = useRouter();
const route = useRoute();

const keyword = ref("");
const showLogoutDialog = ref(false);
const showCart = ref(false);
const hotKws = ["连衣裙", "T恤", "外套", "牛仔裤", "卫衣", "短裙"];
const categories = ref(["上衣", "裤子", "裙子", "外套", "卫衣", "配饰"]);

onMounted(async () => {
  // 已登录时初始化收藏列表（页面刷新后保持星星状态）
  if (auth.isLoggedIn && !favs.loaded) {
    favs.load().catch(() => {});
  }
  try {
    const res = await getCategories();
    if (res.data?.length)
      categories.value = res.data.map((c) => c.name).slice(0, 8);
  } catch (_) {}
});

function doSearch() {
  const kw = keyword.value.trim();
  if (!kw) return;
  // 如果输入的关键词直接匹配某个分类名，则走分类搜索（更精准）
  if (categories.value.includes(kw)) {
    router.push({ path: "/products", query: { category: kw } });
  } else {
    router.push({ path: "/products", query: { keyword: kw } });
  }
}
function quickSearch(kw) {
  keyword.value = kw;
  doSearch();
}
function handleUserMenu(cmd) {
  if (cmd === "profile") router.push("/profile");
  if (cmd === "favorites") router.push("/profile?tab=favorites");
  if (cmd === "logout") showLogoutDialog.value = true;
}
function confirmLogout() {
  showLogoutDialog.value = false;
  auth.logout();
  ElMessage.success("已退出登录");
  router.push("/");
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── 顶部红条 ── */
/* ── 淘宝风格顶部导航 (Site Nav) ── */
.site-nav {
  height: 35px;
  background: #f5f5f5;
  border-bottom: 1px solid #eee;
  font-size: 12px;
  color: #6c6c6c;
  display: flex;
  align-items: center;
}
.site-nav .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.site-nav a,
.site-nav span {
  color: #6c6c6c;
  text-decoration: none;
}
.site-nav a:hover,
.nav-link:hover {
  color: #ff5000;
}
.nav-left,
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.welcome-text {
  margin-right: 15px;
}
.login-link {
  font-weight: bold;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: color 0.1s;
}
.cart-link {
  position: relative;
}
.cart-count {
  margin-left: 2px;
}
.site-nav .divider {
  width: 1px;
  height: 12px;
  background: #ddd;
  margin: 0 4px;
}

/* ── 淘宝主头部 ── */
.main-header {
  background: #fff;
  padding: 30px 0 25px;
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none !important;
}
.logo-icon {
  font-size: 46px;
}
.logo-text {
  display: flex;
  flex-direction: column;
}
.logo-main {
  font-size: 28px;
  font-weight: 900;
  letter-spacing: 2px;
}
.logo-sub {
  font-size: 12px;
  color: #999;
  letter-spacing: 6px;
  margin-top: 2px;
}

/* 淘宝大搜索框 */
.search-wrap {
  flex: 1;
  max-width: 700px;
  margin-left: 60px;
  display: flex;
  flex-direction: column;
}
.tb-search {
  display: flex;
  width: 100%;
  border: 2px solid #ff5000;
  border-radius: 40px;
  overflow: hidden;
  height: 40px;
}
.tb-search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0 20px;
  font-size: 14px;
  color: #333;
}
.tb-search-btn {
  width: 100px;
  background: #ff5000;
  color: #fff;
  border: none;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 4px;
  text-align: center;
  transition: background 0.2s;
}
.tb-search-btn:hover {
  background: #ff7333;
}
.hot-keywords {
  margin-top: 8px;
  padding-left: 16px;
  display: flex;
  gap: 12px;
}
.kw-tag {
  font-size: 12px;
  color: #999;
  cursor: pointer;
}
.kw-tag:hover {
  color: #ff5000;
}

/* ── 分类导航 (主导航条) ── */
.category-nav {
  background: #ff5000;
  height: 38px;
  font-size: 15px;
  font-weight: 600;
}
.category-nav .container {
  height: 100%;
}
.cat-list {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
.cat-item {
  display: flex;
  align-items: center;
  padding: 0 24px;
  color: #fff;
  text-decoration: none;
  transition: background 0.2s;
  cursor: pointer;
  height: 100%;
}
.cat-item:hover,
.cat-item.active {
  background: #d94400;
  color: #fff;
}

/* ── 主内容 ── */
.main-content {
  flex: 1;
  padding: 20px 0 40px;
}

/* ── Footer ── */
.footer {
  background: #2c2c2c;
  color: #888;
  padding: 20px 0;
  text-align: center;
  font-size: 13px;
  line-height: 2;
}
.footer a {
  color: #aaa;
}
.footer a:hover {
  color: #fff;
}
.footer-links {
  margin-bottom: 8px;
}
.footer .divider {
  margin: 0 10px;
}
.dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px 4px;
}
.dropdown-uname {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
