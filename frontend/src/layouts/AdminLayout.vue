<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" class="admin-aside">
      <div class="admin-logo">⚙️ 管理后台</div>
      <el-menu
        :router="true"
        :default-active="$route.path"
        background-color="#2c3e50"
        text-color="#bdc3c7"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/admin" v-if="auth.isAdmin"
          >📊 数据概览</el-menu-item
        >
        <el-menu-item index="/admin/products">👗 商品管理</el-menu-item>>
        <el-menu-item index="/">← 返回前台</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="admin-header">
        <span>欢迎，{{ auth.user?.username }}</span>
        <el-button @click="logout" type="danger" size="small">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useAuthStore } from "../store/auth";
import { useRouter } from "vue-router";
const auth = useAuthStore();
const router = useRouter();
function logout() {
  auth.logout();
  router.push("/");
}
</script>

<style scoped>
.admin-aside {
  background: #2c3e50;
}
.admin-logo {
  color: #fff;
  text-align: center;
  padding: 20px 0;
  font-size: 18px;
  font-weight: 700;
}
.admin-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
}
</style>
