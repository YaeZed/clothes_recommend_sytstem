<template>
  <div class="admin-dashboard" v-loading="loading">
    <!-- 顶部概览卡片 -->
    <div class="stat-cards">
      <div class="stat-card" v-for="s in statCards" :key="s.label">
        <div class="sc-icon">{{ s.icon }}</div>
        <div class="sc-body">
          <div class="sc-num">{{ s.value }}</div>
          <div class="sc-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- 行为分布 -->
    <div class="section-card">
      <div class="section-title">📊 用户行为分布</div>
      <div class="behavior-grid">
        <div
          class="bhv-item"
          v-for="(count, type) in stats.behaviorStats"
          :key="type"
        >
          <div class="bhv-bar-wrap">
            <div
              class="bhv-bar"
              :style="{
                width: barWidth(count) + '%',
                background: bhvColor[type],
              }"
            />
          </div>
          <div class="bhv-meta">
            <span class="bhv-label">{{ TYPE_LABEL[type] || type }}</span>
            <strong>{{ count }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="section-card">
      <div class="section-title">🔧 快捷管理</div>
      <div class="quick-grid">
        <router-link to="/admin/products" class="quick-item">
          <span>👗</span><span>商品管理</span>
        </router-link>
        <div class="quick-item" @click="$router.push('/products')">
          <span>🛍️</span><span>浏览商城</span>
        </div>
        <div class="quick-item" @click="$router.push('/')">
          <span>🏠</span><span>回到首页</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import request from "../../api/request";

const loading = ref(false);
const stats = ref({ userCount: 0, productCount: 0, behaviorStats: {} });

const TYPE_LABEL = {
  view: "👀 浏览",
  collect: "⭐ 收藏",
  cart: "🛒 加购",
  purchase: "✅ 购买",
};
const bhvColor = {
  view: "#74b9ff",
  collect: "#fdcb6e",
  cart: "#fd79a8",
  purchase: "#55efc4",
};

const totalBehavior = computed(() =>
  Object.values(stats.value.behaviorStats).reduce((a, b) => a + b, 0),
);

const statCards = computed(() => [
  { icon: "👤", label: "注册用户", value: stats.value.userCount || 0 },
  { icon: "👗", label: "在售商品", value: stats.value.productCount || 0 },
  { icon: "🔥", label: "总互动次数", value: totalBehavior.value },
  {
    icon: "✅",
    label: "购买次数",
    value: stats.value.behaviorStats?.purchase || 0,
  },
]);

function barWidth(count) {
  const max = Math.max(...Object.values(stats.value.behaviorStats));
  return max ? Math.round((count / max) * 100) : 0;
}

onMounted(async () => {
  loading.value = true;
  try {
    const res = await request.get("/admin/stats");
    stats.value = res.data;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
/* ── 概览卡片 ── */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition);
}
.stat-card:hover {
  box-shadow: var(--shadow-md);
}
.sc-icon {
  font-size: 36px;
}
.sc-num {
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
  line-height: 1;
}
.sc-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* ── 区块 ── */
.section-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 18px;
}

/* ── 行为分布 ── */
.behavior-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.bhv-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.bhv-bar-wrap {
  flex: 1;
  height: 12px;
  background: #f0f0f0;
  border-radius: 100px;
  overflow: hidden;
}
.bhv-bar {
  height: 100%;
  border-radius: 100px;
  transition: width 0.6s ease;
}
.bhv-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 120px;
}
.bhv-label {
  font-size: 13px;
  color: var(--text-secondary);
}
.bhv-meta strong {
  font-size: 14px;
  color: var(--text-primary);
}

/* ── 快捷入口 ── */
.quick-grid {
  display: flex;
  gap: 12px;
}
.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 32px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all var(--transition);
}
.quick-item span:first-child {
  font-size: 28px;
}
.quick-item:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-bg);
  box-shadow: var(--shadow-sm);
}
</style>
