<template>
  <div
    class="product-card"
    @click="goDetail"
    :id="`product-card-${product.id}`"
  >
    <!-- 图片区域 -->
    <div class="card-img-wrap">
      <img
        :src="imgSrc"
        :alt="product.title"
        class="card-img"
        @error="imgSrc = fallbackImg"
        loading="lazy"
      />
      <!-- 标签 -->
      <span class="tag-style" v-if="product.style">{{ product.style }}</span>
      <!-- 收藏按钮 -->
      <button
        class="fav-btn"
        :class="{ active: isFaved }"
        @click.stop="toggleFav"
        v-if="auth.isLoggedIn"
        :id="`fav-btn-${product.id}`"
      >
        <el-icon :color="isFaved ? '#ff5000' : '#bbb'">
          <StarFilled v-if="isFaved" /><Star v-else />
        </el-icon>
      </button>
      <!-- 销量高标记 -->
      <span class="hot-badge" v-if="product.salesCount > 300">热销</span>
    </div>

    <!-- 信息区域 -->
    <div class="card-info">
      <div class="card-title" :title="product.title">{{ product.title }}</div>
      <!-- 标签 -->
      <div class="card-tags" v-if="product.tags?.length">
        <span
          v-for="tag in product.tags.slice(0, 2)"
          :key="tag"
          class="mini-tag"
          >{{ tag }}</span
        >
      </div>
      <div class="card-bottom">
        <div class="card-price">
          <span class="price-symbol">¥</span>
          <span class="price-int">{{ priceInt }}</span>
          <span class="price-dec">.{{ priceDec }}</span>
        </div>
        <span class="card-sales">{{ product.salesCount }}件已售</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import { useFavStore } from "../store/favorites";
import { recordBehavior } from "../api/behavior";
import { Star, StarFilled } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

const props = defineProps({
  product: { type: Object, required: true },
});

const router = useRouter();
const auth = useAuthStore();
const favs = useFavStore();

const fallbackImg =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25'%3E%3Crect width='100%25' height='100%25' fill='%23eeeeee'/%3E%3Ctext x='50%25' y='50%25' fill='%23999999' font-family='sans-serif' font-size='14' text-anchor='middle' dominant-baseline='middle'%3ENo Image%3C/text%3E%3C/svg%3E";
const imgSrc = ref(props.product.images?.[0] || fallbackImg);

// 收藏状态从全局 store 读取（刷新后依然保持）
const isFaved = computed(() => favs.isFaved(props.product.id));

const price = computed(() => Number(props.product.price) || 0);
const priceInt = computed(() => Math.floor(price.value));
const priceDec = computed(() => (price.value % 1).toFixed(2).slice(2));

async function goDetail() {
  if (auth.isLoggedIn) {
    recordBehavior({
      productId: props.product.id,
      actionType: "view",
      duration: 0,
    }).catch(() => {});
  }
  router.push({ name: "ProductDetail", params: { id: props.product.id } });
}

async function toggleFav() {
  if (!auth.isLoggedIn) return;
  try {
    const nowFaved = await favs.toggle(props.product.id);
    ElMessage({
      message: nowFaved ? "⭐ 已收藏" : "取消收藏",
      type: nowFaved ? "success" : "info",
      duration: 1200,
    });
  } catch (_) {
    ElMessage.error("操作失败，请重试");
  }
}
</script>

<style scoped>
.product-card {
  background: #fff;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  border: 1px solid transparent; /* Prepare for hover border */
  transition:
    transform var(--transition),
    box-shadow var(--transition),
    border var(--transition);
  box-shadow: var(--shadow-sm);
}
.product-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: #ff5000; /* Taobao orange hover border */
}

/* 图片 */
.card-img-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  background: #f9f9f9;
  overflow: hidden;
}
.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.product-card:hover .card-img {
  transform: scale(1.05);
}

.tag-style {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(255, 68, 0, 0.85);
  color: #fff;
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 100px;
  backdrop-filter: blur(2px);
}
.hot-badge {
  position: absolute;
  top: 8px;
  right: 40px;
  background: linear-gradient(135deg, #ff4400, #ff8800);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 100px;
}
.fav-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #bbb;
  transition: color var(--transition);
  backdrop-filter: blur(4px);
}
.fav-btn:hover,
.fav-btn.active {
  color: var(--primary);
}

/* 信息 */
.card-info {
  padding: 10px 10px 12px;
}
.card-title {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-primary);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 6px;
  min-height: 40px;
}
.card-tags {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}
.mini-tag {
  font-size: 10px;
  color: #888;
  background: #f5f5f5;
  padding: 1px 6px;
  border-radius: 3px;
}
.card-bottom {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}
.card-price {
  color: var(--primary);
  display: flex;
  align-items: baseline;
  gap: 1px;
}
.price-symbol {
  font-size: 12px;
}
.price-int {
  font-size: 20px;
  font-weight: 700;
}
.price-dec {
  font-size: 12px;
}
.card-sales {
  font-size: 11px;
  color: #bbb;
}
</style>
