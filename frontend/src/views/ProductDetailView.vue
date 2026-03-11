<template>
  <div class="detail-page" v-if="product">
    <!-- 面包屑 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/products' }">商品</el-breadcrumb-item>
      <el-breadcrumb-item>{{ product.category }}</el-breadcrumb-item>
      <el-breadcrumb-item
        >{{ product.title.slice(0, 16) }}...</el-breadcrumb-item
      >
    </el-breadcrumb>

    <!-- 主区域 -->
    <div class="detail-main">
      <!-- 左：图片 -->
      <div class="img-section">
        <div class="main-img">
          <img :src="currentImg" :alt="product.title" />
        </div>
        <div class="thumb-row" v-if="product.images?.length > 1">
          <div
            v-for="(img, i) in product.images"
            :key="i"
            class="thumb"
            :class="{ active: currentImg === img }"
            @click="currentImg = img"
          >
            <img :src="img" />
          </div>
        </div>
      </div>

      <!-- 右：信息 -->
      <div class="info-section">
        <div class="info-top">
          <h1 class="prod-title">{{ product.title }}</h1>
          <div class="prod-meta">
            <el-tag size="small">{{ product.category }}</el-tag>
            <el-tag size="small" type="success">{{ product.style }}</el-tag>
            <span class="sales-count">{{ product.salesCount }} 件已售</span>
          </div>
        </div>

        <!-- 价格区 -->
        <div class="price-block">
          <div class="price-row">
            <span class="price-label">价格</span>
            <div class="big-price">
              <span class="psym">¥</span>
              <span class="pint">{{ Math.floor(product.price) }}</span>
              <span class="pdec"
                >.{{ (product.price % 1).toFixed(2).slice(2) }}</span
              >
            </div>
          </div>
        </div>

        <!-- 属性选择 -->
        <div class="attr-block" v-if="product.attributes">
          <div class="attr-row" v-if="product.attributes.color">
            <span class="attr-label">颜色</span>
            <div class="attr-opts">
              <span
                v-for="c in colorOpts"
                :key="c"
                class="attr-opt"
                :class="{ selected: selectedColor === c }"
                @click="selectedColor = c"
                >{{ c }}</span
              >
            </div>
          </div>
          <div class="attr-row" v-if="product.attributes.size">
            <span class="attr-label">尺码</span>
            <div class="attr-opts">
              <span
                v-for="s in sizeOpts"
                :key="s"
                class="attr-opt"
                :class="{ selected: selectedSize === s }"
                @click="selectedSize = s"
                >{{ s }}</span
              >
            </div>
          </div>
        </div>

        <!-- 库存 -->
        <div class="stock-row">
          <span class="attr-label">库存</span>
          <span :class="product.stock > 50 ? 'in-stock' : 'low-stock'">
            {{ product.stock > 50 ? "现货充足" : `仅剩 ${product.stock} 件` }}
          </span>
        </div>

        <!-- 按钮 -->
        <div class="action-btns">
          <el-button class="btn-cart" size="large" @click="addToCart"
            >加入购物车</el-button
          >
          <el-button type="primary" class="btn-buy" size="large" @click="buyNow"
            >立即购买</el-button
          >
          <el-button
            class="btn-fav"
            :type="isFaved ? 'danger' : 'default'"
            size="large"
            @click="toggleFav"
          >
            <el-icon :color="isFaved ? '#ff4400' : ''"
              ><StarFilled v-if="isFaved" /><Star v-else
            /></el-icon>
            {{ isFaved ? "已收藏" : "收藏" }}
          </el-button>
        </div>

        <!-- 标签 -->
        <div class="tags-row" v-if="product.tags?.length">
          <span class="attr-label">标签</span>
          <el-tag
            v-for="t in product.tags"
            :key="t"
            size="small"
            type="info"
            class="m-tag"
            >{{ t }}</el-tag
          >
        </div>
      </div>
    </div>

    <!-- 商品描述 -->
    <div class="desc-card" v-if="product.description">
      <div class="desc-title">宝贝详情</div>
      <p class="desc-text">{{ product.description }}</p>
    </div>

    <!-- 用户评价 -->
    <div class="comments-card">
      <div class="desc-title">宝贝评价 (0)</div>
      <div class="comments-empty">
        <el-empty
          description="暂无评价，购买后快来抢沙发吧～"
          :image-size="80"
        />
      </div>
    </div>

    <!-- 相似推荐 -->
    <div class="similar-section">
      <div class="section-head">
        <h2>✨ 相似推荐</h2>
      </div>
      <ProductGrid
        :products="similar"
        :loading="loadingSimilar"
        :skeleton-count="5"
      />
    </div>
  </div>

  <!-- 加载中 -->
  <div v-else class="detail-loading">
    <el-skeleton :rows="8" animated />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import { useFavStore } from "../store/favorites";
import { useCartStore } from "../store/cart";
import { getProduct } from "../api/product";
import { getSimilarRecommend } from "../api/recommend";
import { recordBehavior } from "../api/behavior";
import ProductGrid from "../components/ProductGrid.vue";
import { Star, StarFilled } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const favs = useFavStore();
const cart = useCartStore();

const product = ref(null);
const similar = ref([]);
const loadingSimilar = ref(false);
const currentImg = ref("");
const selectedColor = ref("");
const selectedSize = ref("");

// 从全局 store 读取收藏状态（刷新后依然保持）
const isFaved = computed(() =>
  product.value ? favs.isFaved(product.value.id) : false,
);

const colorOpts = computed(() => {
  const c = product.value?.attributes?.color;
  return c ? (Array.isArray(c) ? c : [c]) : ["白色", "黑色", "蓝色", "红色"];
});
const sizeOpts = computed(() => {
  const s = product.value?.attributes?.size;
  return s ? (Array.isArray(s) ? s : [s]) : ["S", "M", "L", "XL"];
});

async function load(id) {
  const res = await getProduct(id);
  product.value = res.data;
  currentImg.value = product.value.images?.[0] || "";

  // 默认选中第一个颜色和尺码
  if (colorOpts.value.length) selectedColor.value = colorOpts.value[0];
  if (sizeOpts.value.length) selectedSize.value = sizeOpts.value[0];
  selectedColor.value = colorOpts.value[0] || "";
  selectedSize.value = sizeOpts.value[0] || "";

  loadingSimilar.value = true;
  const sRes = await getSimilarRecommend(id, 5);
  similar.value = sRes.data.items;
  loadingSimilar.value = false;
}

async function toggleFav() {
  if (!auth.isLoggedIn) {
    router.push("/auth/login");
    return;
  }
  try {
    const nowFaved = await favs.toggle(product.value.id);
    ElMessage({
      message: nowFaved ? "⭐ 已收藏" : "取消收藏",
      type: nowFaved ? "success" : "info",
      duration: 1200,
    });
  } catch (_) {
    ElMessage.error("操作失败，请重试");
  }
}

async function addToCart() {
  if (!auth.isLoggedIn) {
    router.push("/auth/login");
    return;
  }
  // 加入购物车 store（含选中颜色/尺码）
  cart.addItem(product.value, 1, selectedColor.value, selectedSize.value);
  // 同时记录 cart 行为
  recordBehavior({
    productId: product.value.id,
    actionType: "cart",
    duration: 0,
  }).catch(() => {});
  ElMessage({
    message: "🛒 已加入购物车",
    type: "success",
    duration: 2000,
  });
}

async function buyNow() {
  if (!auth.isLoggedIn) {
    router.push("/auth/login");
    return;
  }
  // 先加入购物车，确保结算页有数据
  await cart.addItem(product.value, 1, selectedColor.value, selectedSize.value);
  // 记录行为
  recordBehavior({
    productId: product.value.id,
    actionType: "cart",
    duration: 0,
  }).catch(() => {});
  // 跳转到结算页
  router.push("/checkout");
}

onMounted(() => load(route.params.id));
watch(
  () => route.params.id,
  (id) => id && load(id),
);
</script>

<style scoped>
.breadcrumb {
  margin-bottom: 16px;
  font-size: 13px;
}
.detail-loading {
  padding: 40px;
  background: #fff;
  border-radius: var(--radius-lg);
}

/* ── 主区域 ── */
.detail-main {
  display: flex;
  gap: 32px;
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 28px;
  margin-bottom: 16px;
}

/* 图片 */
.img-section {
  width: 400px;
  flex-shrink: 0;
}
.main-img {
  width: 400px;
  height: 480px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #f9f9f9;
  margin-bottom: 10px;
}
.main-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumb-row {
  display: flex;
  gap: 8px;
}
.thumb {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color var(--transition);
}
.thumb.active {
  border-color: var(--primary);
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 信息 */
.info-section {
  flex: 1;
  min-width: 0;
}
.prod-title {
  font-size: 18px;
  font-weight: 600;
  line-height: 1.5;
  margin-bottom: 12px;
}
.prod-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.sales-count {
  font-size: 12px;
  color: var(--text-muted);
}

/* 价格 */
.price-block {
  background: #fff5f2;
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  margin-bottom: 20px;
}
.price-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
}
.price-label {
  font-size: 13px;
  color: var(--text-muted);
}
.big-price {
  display: flex;
  align-items: baseline;
  color: var(--primary);
}
.psym {
  font-size: 16px;
}
.pint {
  font-size: 36px;
  font-weight: 800;
  line-height: 1;
}
.pdec {
  font-size: 18px;
}

/* 属性 */
.attr-block {
  margin-bottom: 16px;
}
.attr-row,
.stock-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.attr-label {
  font-size: 13px;
  color: var(--text-muted);
  width: 36px;
  flex-shrink: 0;
}
.attr-opts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.attr-opt {
  padding: 4px 16px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition);
}
.attr-opt:hover {
  border-color: var(--primary);
  color: var(--primary);
}
.attr-opt.selected {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-bg);
}

.in-stock {
  color: #52c41a;
  font-size: 13px;
}
.low-stock {
  color: var(--primary);
  font-size: 13px;
  font-weight: 600;
}

/* 按钮 */
.action-btns {
  display: flex;
  gap: 12px;
  margin: 24px 0;
}
.btn-buy {
  background: #ffeded !important;
  border-color: #ff5000 !important;
  color: #ff5000 !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  padding: 0 40px !important;
  border-radius: 4px !important;
}
.btn-buy:hover {
  background: #ffe4d9 !important;
}
.btn-cart {
  background: #ff5000 !important;
  border-color: #ff5000 !important;
  color: #fff !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  padding: 0 40px !important;
  border-radius: 4px !important;
}
.btn-cart:hover {
  background: #ff7333 !important;
  border-color: #ff7333 !important;
}
.btn-fav {
  padding: 0 20px !important;
  border-radius: 4px !important;
}

.tags-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.m-tag {
  margin: 0;
}

/* ── 描述与评价 ── */
.desc-card,
.comments-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 24px 28px;
  margin-bottom: 16px;
}
.desc-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.desc-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
}

/* ── 相似推荐 ── */
.similar-section {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px 24px;
}
.section-head {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
.section-head h2 {
  font-size: 17px;
  font-weight: 700;
}
</style>
