import { defineStore } from "pinia";
import { ref, computed } from "vue";
import * as authApi from "../api/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("token") || "");
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"));

  const isLoggedIn = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === "admin");
  const isMerchant = computed(() => user.value?.role === "merchant");
  const hasAdminAccess = computed(() => isAdmin.value || isMerchant.value);

  function setAuth(data) {
    token.value = data.token;
    user.value = data.user;
    localStorage.setItem("token", data.token);
    localStorage.setItem("user", JSON.stringify(data.user));
  }

  function clearAuth() {
    token.value = "";
    user.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  }

  async function login(payload) {
    const res = await authApi.login(payload);
    setAuth(res.data);
    // 登录后延迟加载收藏列表和购物车
    import("../store/favorites")
      .then(({ useFavStore }) => useFavStore().load())
      .catch(() => {});
    import("../store/cart")
      .then(({ useCartStore }) => useCartStore().load())
      .catch(() => {});
    return res;
  }

  async function register(payload) {
    const res = await authApi.register(payload);
    setAuth(res.data);
    return res;
  }

  async function fetchProfile() {
    const res = await authApi.getProfile();
    user.value = res.data;
    localStorage.setItem("user", JSON.stringify(res.data));
    return res;
  }

  function logout() {
    clearAuth();
    // 清空收藏状态和购物车
    import("../store/favorites")
      .then(({ useFavStore }) => useFavStore().clear())
      .catch(() => {});
    import("../store/cart")
      .then(({ useCartStore }) => useCartStore().clear())
      .catch(() => {});
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    isMerchant,
    hasAdminAccess,
    login,
    register,
    fetchProfile,
    logout,
  };
});
