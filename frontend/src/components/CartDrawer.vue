<template>
  <!-- 购物车遮罩 -->
  <transition name="overlay-fade">
    <div v-if="visible" class="cart-overlay" @click="emit('close')" />
  </transition>

  <!-- 购物车抽屉 -->
  <transition name="drawer-slide">
    <div v-if="visible" class="cart-drawer">
      <!-- 头部 -->
      <div class="drawer-head">
        <span class="drawer-title">🛒 购物车</span>
        <span class="drawer-count">{{ cart.totalCount }} 件</span>
        <button class="close-btn" @click="emit('close')">✕</button>
      </div>

      <!-- 购物车为空 -->
      <div v-if="!cart.items.length" class="cart-empty">
        <div class="empty-icon">🛍️</div>
        <div class="empty-text">购物车空空如也</div>
        <el-button
          type="primary"
          @click="
            emit('close');
            $router.push('/products');
          "
        >
          去逛逛
        </el-button>
      </div>

      <!-- 商品列表 -->
      <div class="cart-list" v-else>
        <div v-for="(item, idx) in cart.items" :key="idx" class="cart-item">
          <!-- 商品图片 -->
          <img
            :src="item.product?.images?.[0]"
            class="ci-img"
            @click="goDetail(item.product.id)"
            @error="
              $event.target.src =
                'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'100%25\' height=\'100%25\'%3E%3Crect width=\'100%25\' height=\'100%25\' fill=\'%23eeeeee\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' fill=\'%23999999\' font-family=\'sans-serif\' font-size=\'14\' text-anchor=\'middle\' dominant-baseline=\'middle\'%3ENo Image%3C/text%3E%3C/svg%3E'
            "
          />
          <!-- 商品信息 -->
          <div class="ci-body" v-if="item.product">
            <div class="ci-title" @click="goDetail(item.product.id)">
              {{ item.product.title }}
            </div>
            <div
              class="ci-opts"
              v-if="item.attributes?.color || item.attributes?.size"
            >
              <span v-if="item.attributes?.color" class="ci-tag">{{
                item.attributes.color
              }}</span>
              <span v-if="item.attributes?.size" class="ci-tag">{{
                item.attributes.size
              }}</span>
            </div>
            <div class="ci-bottom">
              <span class="ci-price"
                >¥{{
                  (Number(item.product.price) * item.quantity).toFixed(2)
                }}</span
              >
              <div class="ci-qty">
                <button
                  @click="cart.setQty(idx, item.quantity - 1)"
                  class="qty-btn"
                >
                  −
                </button>
                <span class="qty-num">{{ item.quantity }}</span>
                <button
                  @click="cart.setQty(idx, item.quantity + 1)"
                  class="qty-btn"
                >
                  ＋
                </button>
              </div>
            </div>
          </div>
          <!-- 删除 -->
          <button class="ci-del" @click="cart.removeItem(idx)" title="移除">
            ✕
          </button>
        </div>
      </div>

      <!-- 底部结算栏 -->
      <div class="drawer-footer" v-if="cart.items.length">
        <div class="footer-total">
          合计：<strong class="total-price"
            >¥{{ cart.totalPrice.toFixed(2) }}</strong
          >
        </div>
        <el-button
          type="primary"
          class="checkout-btn"
          size="large"
          @click="checkout"
          :loading="checkingOut"
        >
          结算 ({{ cart.totalCount }})
        </el-button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useCartStore } from "../store/cart";
import { useAuthStore } from "../store/auth";
import { createOrder, payOrder } from "../api/order";
import { ElMessage, ElMessageBox } from "element-plus";

const props = defineProps({ visible: Boolean });
const emit = defineEmits(["close"]);
const cart = useCartStore();
const auth = useAuthStore();
const router = useRouter();
const checkingOut = ref(false);

function goDetail(id) {
  emit("close");
  router.push(`/products/${id}`);
}

async function checkout() {
  checkingOut.value = true;
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
      `共 ${cart.totalCount} 件商品，合计 ¥${cart.totalPrice.toFixed(2)}，确认结算？`,
      "确认订单",
      {
        confirmButtonText: "去支付",
        cancelButtonText: "再逛逛",
        type: "warning",
      },
    );

    // 1. 生成订单
    const orderRes = await createOrder({
      receiver: {
        name: auth.user?.username || "收件人",
        phone: "13800138000",
        address: "测试收货地址（可在个人中心修改）",
      },
    });

    const orderId = orderRes.data.data.id;

    // 2. 模拟支付
    await payOrder(orderId);

    // 3. 清空购物车
    await cart.load(); // 或调用 cart.clearAll() 获取最新空状态，由于我们后端已经删除了对应的 cart_items，重新 loaded 即可

    ElMessage({
      message: "🎉 支付成功！已为您生成专属推荐",
      type: "success",
      duration: 3000,
    });

    emit("close");
    // 如果已经在个人中心，可以考虑刷新，否则跳到个人中心的订单列表，为了简化我们去 profile
    router.push("/profile?tab=orders");
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(error.response?.data?.msg || "结算失败");
    }
  } finally {
    checkingOut.value = false;
  }
}
</script>

<style scoped>
/* ── 遮罩 ── */
.cart-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 2000;
}
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.25s;
}
.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* ── 抽屉 ── */
.cart-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 380px;
  height: 100vh;
  background: #fff;
  z-index: 2001;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
}
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(100%);
}

/* 头部 */
.drawer-head {
  display: flex;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid #f0f0f0;
  gap: 8px;
}
.drawer-title {
  font-size: 17px;
  font-weight: 700;
  flex: 1;
}
.drawer-count {
  font-size: 12px;
  color: var(--text-muted);
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 100px;
}
.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #999;
  padding: 4px;
  margin-left: 8px;
}
.close-btn:hover {
  color: var(--text-primary);
}

/* 空状态 */
.cart-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
}
.empty-icon {
  font-size: 56px;
}
.empty-text {
  font-size: 15px;
}

/* 商品列表 */
.cart-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}
.cart-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #f8f8f8;
  position: relative;
  transition: background var(--transition);
}
.cart-item:hover {
  background: #fafafa;
}

.ci-img {
  width: 72px;
  height: 88px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  flex-shrink: 0;
  background: #f0f0f0;
}
.ci-body {
  flex: 1;
  min-width: 0;
}
.ci-title {
  font-size: 13px;
  line-height: 1.4;
  font-weight: 500;
  cursor: pointer;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 6px;
}
.ci-title:hover {
  color: var(--primary);
}

.ci-opts {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}
.ci-tag {
  font-size: 11px;
  color: #888;
  background: #f5f5f5;
  padding: 1px 6px;
  border-radius: 3px;
}

.ci-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ci-price {
  font-size: 15px;
  font-weight: 700;
  color: var(--primary);
}
.ci-qty {
  display: flex;
  align-items: center;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  overflow: hidden;
}
.qty-btn {
  width: 26px;
  height: 26px;
  border: none;
  background: #f7f7f7;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  transition: background var(--transition);
}
.qty-btn:hover {
  background: var(--primary-bg);
  color: var(--primary);
}
.qty-num {
  width: 32px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
}

.ci-del {
  position: absolute;
  top: 10px;
  right: 12px;
  background: none;
  border: none;
  font-size: 13px;
  color: #ccc;
  cursor: pointer;
  padding: 2px;
}
.ci-del:hover {
  color: var(--primary);
}

/* 底部结算 */
.drawer-footer {
  padding: 14px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #fff;
}
.footer-total {
  font-size: 14px;
  color: var(--text-secondary);
}
.total-price {
  font-size: 20px;
  font-weight: 800;
  color: var(--primary);
}
.checkout-btn {
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  padding: 0 24px !important;
  flex-shrink: 0;
}
</style>
