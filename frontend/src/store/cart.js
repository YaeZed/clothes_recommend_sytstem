/**
 * cart.js  ——  购物车状态管理（localStorage 持久化）
 * 不依赖后端，数据存在浏览器本地。
 * 退出登录时清空购物车。
 */
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useAuthStore } from "./auth";
import * as cartApi from "../api/cart";
import { ElMessage } from "element-plus";

export const useCartStore = defineStore("cart", () => {
  const auth = useAuthStore();
  const items = ref([]);
  const loading = ref(false);

  const totalCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0),
  );

  const totalPrice = computed(() =>
    items.value.reduce(
      (sum, item) => sum + Number(item.product?.price || 0) * item.quantity,
      0,
    ),
  );

  async function load() {
    if (!auth.isLoggedIn) {
      items.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await cartApi.getCart();
      items.value = res.data || [];
    } catch (e) {
      console.error("加载购物车失败", e);
    } finally {
      loading.value = false;
    }
  }

  async function addItem(
    product,
    qty = 1,
    selectedColor = "",
    selectedSize = "",
  ) {
    if (!auth.isLoggedIn) {
      ElMessage.warning("请先登录");
      return;
    }
    try {
      await cartApi.addToCart({
        productId: product.id,
        quantity: qty,
        attributes: { color: selectedColor, size: selectedSize },
      });
      ElMessage.success("已加入购物车");
      await load();
    } catch (e) {
      ElMessage.error(e.response?.data?.msg || "添加失败");
    }
  }

  async function setQty(itemIdx, newQty) {
    const item = items.value[itemIdx];
    if (!item) return;
    if (newQty <= 0) {
      await removeItem(itemIdx);
      return;
    }
    try {
      await cartApi.updateCartItem(item.id, newQty);
      item.quantity = newQty;
    } catch (e) {
      ElMessage.error(e.response?.data?.msg || "修改失败");
      await load(); // 恢复原始数据
    }
  }

  async function removeItem(itemIdx) {
    const item = items.value[itemIdx];
    if (!item) return;
    try {
      await cartApi.removeCartItem(item.id);
      items.value.splice(itemIdx, 1);
    } catch (e) {
      ElMessage.error("移除失败");
    }
  }

  async function clear() {
    if (!auth.isLoggedIn) return;
    try {
      await cartApi.clearCart();
      items.value = [];
    } catch (e) {
      ElMessage.error("清空失败");
    }
  }

  return {
    items,
    loading,
    totalCount,
    totalPrice,
    load,
    addItem,
    setQty,
    removeItem,
    clear,
  };
});
