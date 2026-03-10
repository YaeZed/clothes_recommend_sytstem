<template>
  <div class="product-grid-wrap">
    <!-- Loading 骨架 -->
    <div v-if="loading" class="product-grid">
      <div v-for="i in skeletonCount" :key="i" class="skeleton-card">
        <div class="sk-img"></div>
        <div class="sk-line long"></div>
        <div class="sk-line short"></div>
        <div class="sk-line price"></div>
      </div>
    </div>

    <!-- 商品网格 -->
    <div v-else-if="products?.length" class="product-grid">
      <ProductCard v-for="p in products" :key="p.id" :product="p" />
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty :description="emptyText" :image-size="120" />
    </div>
  </div>
</template>

<script setup>
import ProductCard from "./ProductCard.vue";

defineProps({
  products: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  skeletonCount: { type: Number, default: 10 },
  emptyText: { type: String, default: "暂无商品" },
});
</script>

<style scoped>
.product-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

@media (max-width: 1100px) {
  .product-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
@media (max-width: 860px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 560px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 骨架 */
.skeleton-card {
  background: #fff;
  border-radius: var(--radius-md);
  overflow: hidden;
  padding-bottom: 14px;
}
.sk-img {
  width: 100%;
  aspect-ratio: 3/4;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.sk-line {
  margin: 8px 10px 0;
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.sk-line.long {
  width: 80%;
}
.sk-line.short {
  width: 55%;
}
.sk-line.price {
  width: 40%;
  height: 16px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.empty-state {
  padding: 60px 0;
}
</style>
