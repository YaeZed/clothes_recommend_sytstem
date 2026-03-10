<template>
  <div class="auth-page">
    <div class="auth-brand">
      <router-link to="/" class="brand-logo">👗 穿搭推荐</router-link>
      <p>AI 智能穿搭推荐平台</p>
    </div>
    <div class="auth-card">
      <h2 class="auth-title">注册账号</h2>
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名（4-20位）"
            size="large"
            prefix-icon="User"
            id="reg-username"
          />
        </el-form-item>
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="邮箱（选填）"
            size="large"
            prefix-icon="Message"
            id="reg-email"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码（至少6位）"
            size="large"
            prefix-icon="Lock"
            show-password
            id="reg-password"
          />
        </el-form-item>
        <el-form-item label="风格偏好">
          <el-checkbox-group v-model="form.stylePref">
            <el-checkbox v-for="s in styleOptions" :key="s" :label="s">{{
              s
            }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="auth-btn"
          :loading="loading"
          @click="doRegister"
          id="reg-submit-btn"
        >
          立即注册
        </el-button>
      </el-form>
      <div class="auth-footer">
        已有账号？<router-link to="/auth/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import { ElMessage } from "element-plus";

const router = useRouter();
const auth = useAuthStore();

const formRef = ref();
const loading = ref(false);
const styleOptions = [
  "休闲",
  "正式",
  "运动",
  "街头",
  "森系",
  "复古",
  "简约",
  "潮流",
];
const form = ref({ username: "", email: "", password: "", stylePref: [] });
const rules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 2, max: 20, message: "用户名 2-20 位", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码至少 6 位", trigger: "blur" },
  ],
};

async function doRegister() {
  await formRef.value.validate();
  loading.value = true;
  try {
    await auth.register(form.value);
    ElMessage.success("注册成功，欢迎加入！");
    router.push("/");
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || "注册失败");
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
  max-width: 420px;
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 36px 40px;
  box-shadow: var(--shadow-lg);
}
.auth-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 24px;
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
