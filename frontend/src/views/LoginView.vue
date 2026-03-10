<template>
  <div class="auth-page">
    <div class="auth-brand">
      <router-link to="/" class="brand-logo">👗 穿搭推荐</router-link>
      <p>AI 智能穿搭推荐平台</p>
    </div>
    <div class="auth-card">
      <h2 class="auth-title">登录账号</h2>
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        @submit.prevent="doLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            prefix-icon="User"
            id="login-username"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
            id="login-password"
            @keyup.enter="doLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="auth-btn"
          :loading="loading"
          @click="doLogin"
          id="login-submit-btn"
          >立即登录</el-button
        >
      </el-form>
      <div class="auth-footer">
        还没有账号？<router-link to="/auth/register">免费注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../store/auth";
import { ElMessage } from "element-plus";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const formRef = ref();
const loading = ref(false);
const form = ref({ username: "", password: "" });
const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

async function doLogin() {
  await formRef.value.validate();
  loading.value = true;
  try {
    await auth.login(form.value);
    ElMessage.success("登录成功！");
    const redirect = route.query.redirect || "/";
    router.push(redirect);
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || "登录失败，请检查用户名或密码");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff5f2 0%, #fff 100%);
  padding: 40px 16px;
}
.auth-brand {
  text-align: center;
  margin-bottom: 24px;
}
.brand-logo {
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
  letter-spacing: 1px;
}
.auth-brand p {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 6px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 36px 40px;
  box-shadow: var(--shadow-lg);
}
.auth-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--text-primary);
}
.auth-btn {
  width: 100%;
  font-size: 16px !important;
  font-weight: 600 !important;
  height: 46px !important;
  margin-top: 4px;
  background: #ff5000 !important;
  border-color: #ff5000 !important;
  border-radius: 4px !important;
}
.auth-btn:hover {
  background: #ff7333 !important;
  border-color: #ff7333 !important;
}
.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: var(--text-muted);
}
.auth-footer a {
  color: var(--primary);
  font-weight: 600;
}
</style>
