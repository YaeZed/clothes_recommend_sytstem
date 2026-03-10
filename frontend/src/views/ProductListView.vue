<template>
  <div>
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <!-- 分类 -->
      <div class="filter-group">
        <span class="filter-label">分类</span>
        <div class="filter-opts">
          <span
            class="filter-opt"
            :class="{ active: !filters.category }"
            @click="setFilter('category', '')"
            >全部</span
          >
          <span
            v-for="c in categories"
            :key="c.name"
            class="filter-opt"
            :class="{ active: filters.category === c.name }"
            @click="setFilter('category', c.name)"
            >{{ c.name }}</span
          >
        </div>
      </div>

      <!-- 风格 -->
      <div class="filter-group">
        <span class="filter-label">风格</span>
        <div class="filter-opts">
          <span
            class="filter-opt"
            :class="{ active: !filters.style }"
            @click="setFilter('style', '')"
            >全部</span
          >
          <span
            v-for="s in styles"
            :key="s.name"
            class="filter-opt"
            :class="{ active: filters.style === s.name }"
            @click="setFilter('style', s.name)"
            >{{ s.name }}</span
          >
        </div>
      </div>

      <!-- 排序 -->
      <div class="filter-group sort-row">
        <span class="filter-label">排序</span>
        <div class="sort-btns">
          <button
            v-for="s in sorts"
            :key="s.value"
            class="sort-btn"
            :class="{ active: filters.sortBy === s.value }"
            @click="setFilter('sortBy', s.value)"
          >
            {{ s.label }}
          </button>
        </div>
        <!-- 搜索词提示 -->
        <div v-if="filters.keyword" class="keyword-bar">
          搜索：<strong>"{{ filters.keyword }}"</strong>
          <span class="clear-kw" @click="clearKeyword">✕</span>
        </div>
      </div>
    </div>

    <!-- 结果统计 -->
    <div class="result-meta" v-if="!loading">
      共 <strong>{{ total }}</strong> 件商品
    </div>

    <!-- 商品列表 -->
    <ProductGrid :products="products" :loading="loading" :skeleton-count="20" />

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > perPage">
      <el-pagination
        v-model:current-page="page"
        :page-size="perPage"
        :total="total"
        layout="prev, pager, next"
        background
        @change="fetchProducts"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getProducts, getCategories, getStyles } from "../api/product";
import ProductGrid from "../components/ProductGrid.vue";

const route = useRoute();
const router = useRouter();

const products = ref([]);
const loading = ref(false);
const total = ref(0);
const page = ref(1);
const perPage = 20;

const categories = ref([]);
const styles = ref([]);

const filters = reactive({
  keyword: "",
  category: "",
  style: "",
  sortBy: "sales_count",
});

const sorts = [
  { label: "综合", value: "sales_count" },
  { label: "最新", value: "newest" },
  { label: "价格↑", value: "price_asc" },
  { label: "价格↓", value: "price_desc" },
];

function syncFromRoute() {
  filters.keyword = route.query.keyword || "";
  filters.category = route.query.category || "";
  filters.style = route.query.style || "";
  filters.sortBy = route.query.sortBy || "sales_count";
  page.value = parseInt(route.query.page || "1");
}

async function fetchProducts() {
  loading.value = true;
  try {
    const params = {
      keyword: filters.keyword,
      category: filters.category,
      style: filters.style,
      sortBy: filters.sortBy,
      page: page.value,
      perPage,
    };
    // 同步 URL
    router.replace({
      query: Object.fromEntries(Object.entries(params).filter(([, v]) => v)),
    });
    const res = await getProducts(params);
    products.value = res.data.items;
    total.value = res.data.total;
  } finally {
    loading.value = false;
  }
}

function setFilter(key, val) {
  filters[key] = val;
  page.value = 1;
  fetchProducts();
}

function clearKeyword() {
  filters.keyword = "";
  page.value = 1;
  fetchProducts();
}

onMounted(async () => {
  syncFromRoute();
  const [catRes, styRes] = await Promise.all([getCategories(), getStyles()]);
  categories.value = catRes.data || [];
  styles.value = styRes.data || [];
  fetchProducts();
});

watch(
  () => route.query,
  () => {
    syncFromRoute();
    fetchProducts();
  },
  { deep: true },
);
</script>

<style scoped>
/* ── 筛选栏 ── */
.filter-bar {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  margin-bottom: 16px;
}
.filter-group {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}
.filter-group:last-child {
  border-bottom: none;
}
.filter-label {
  font-size: 13px;
  color: var(--text-muted);
  width: 36px;
  flex-shrink: 0;
  padding-top: 4px;
}
.filter-opts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.filter-opt {
  padding: 4px 14px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.2s;
}
.filter-opt:hover {
  color: #ff5000;
  background: #fff3e8;
}
.filter-opt.active {
  color: #fff;
  background: #ff5000;
  font-weight: bold;
}

.sort-row {
  align-items: center;
  margin-top: 10px;
  padding-top: 12px;
  border-top: 1px dashed #eee;
}
.sort-btns {
  display: flex;
}
.sort-btn {
  padding: 6px 20px;
  border: 1px solid #e8e8e8;
  background: #fff;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: -1px; /* border overlap */
}
.sort-btn:first-child {
  border-top-left-radius: 2px;
  border-bottom-left-radius: 2px;
}
.sort-btn:last-child {
  border-top-right-radius: 2px;
  border-bottom-right-radius: 2px;
}
.sort-btn:hover {
  color: #ff5000;
  position: relative;
  z-index: 1;
  border-color: #ff5000;
}
.sort-btn.active {
  background: #ff5000;
  color: #fff;
  border-color: #ff5000;
  position: relative;
  z-index: 2;
}

.keyword-bar {
  margin-left: 12px;
  font-size: 13px;
  color: var(--text-secondary);
  background: #fff5f2;
  padding: 3px 12px;
  border-radius: 100px;
}
.clear-kw {
  margin-left: 8px;
  cursor: pointer;
  color: #bbb;
}
.clear-kw:hover {
  color: var(--primary);
}

/* ── 统计 & 分页 ── */
.result-meta {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
}
.result-meta strong {
  color: var(--primary);
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 32px 0 8px;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background: var(--primary) !important;
}
</style>
