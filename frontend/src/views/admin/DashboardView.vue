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

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 1. 算法评估指标 -->
      <div class="section-card chart-item">
        <div class="section-title">🏆 推荐算法性能对比 (Precision/Recall/NDCG)</div>
        <div ref="algoChartRef" class="chart-container"></div>
      </div>

      <!-- 2. 品类分布 -->
      <div class="section-card chart-item">
        <div class="section-title">📊 商品品类分布统计</div>
        <div ref="categoryChartRef" class="chart-container"></div>
      </div>

      <!-- 3. 近7日活跃趋势 -->
      <div class="section-card chart-full">
        <div class="section-title">📈 近 7 日用户行为活跃趋势</div>
        <div ref="trendChartRef" class="chart-container trend-chart"></div>
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
import { ref, computed, onMounted, nextTick } from "vue";
import request from "../../api/request";
import * as echarts from "echarts";

const loading = ref(false);
const stats = ref({
  userCount: 0,
  productCount: 0,
  behaviorStats: {},
  categoryStats: {},
  behaviorTrend: {},
  algoMetrics: {},
});

const algoChartRef = ref(null);
const categoryChartRef = ref(null);
const trendChartRef = ref(null);

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

// ── 初始化图表 ──
function initAlgoChart() {
  if (!algoChartRef.value) return;
  const chart = echarts.init(algoChartRef.value);
  const metrics = stats.value.algoMetrics;
  const algos = Object.keys(metrics);
  const p10 = algos.map((a) => metrics[a]["Precision@10"]);
  const r10 = algos.map((a) => metrics[a]["Recall@10"]);
  const n10 = algos.map((a) => metrics[a]["NDCG@10"]);

  chart.setOption({
    tooltip: { trigger: "axis" },
    legend: { data: ["Precision@10", "Recall@10", "NDCG@10"], bottom: 0 },
    grid: { top: 30, left: 40, right: 20, bottom: 60 },
    xAxis: { type: "category", data: algos },
    yAxis: { type: "value" },
    series: [
      { name: "Precision@10", type: "bar", data: p10, itemStyle: { color: "#ff5000" } },
      { name: "Recall@10", type: "bar", data: r10, itemStyle: { color: "#ff8c00" } },
      { name: "NDCG@10", type: "bar", data: n10, itemStyle: { color: "#ffc900" } },
    ],
  });
}

function initCategoryChart() {
  if (!categoryChartRef.value) return;
  const chart = echarts.init(categoryChartRef.value);
  const data = Object.entries(stats.value.categoryStats).map(([name, value]) => ({
    name,
    value,
  }));

  chart.setOption({
    tooltip: { trigger: "item" },
    legend: { orient: "vertical", left: "left", top: "center" },
    series: [
      {
        name: "品类分布",
        type: "pie",
        radius: ["40%", "70%"],
        center: ["60%", "50%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 8, borderColor: "#fff", borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: "bold" } },
        data: data,
      },
    ],
  });
}

function initTrendChart() {
  if (!trendChartRef.value) return;
  const chart = echarts.init(trendChartRef.value);
  const trend = stats.value.behaviorTrend;
  const dates = Object.keys(trend).sort();
  const views = dates.map((d) => trend[d].view || 0);
  const carts = dates.map((d) => trend[d].cart || 0);
  const buys = dates.map((d) => trend[d].purchase || 0);

  chart.setOption({
    tooltip: { trigger: "axis" },
    legend: { data: ["浏览", "加购", "购买"], right: 20 },
    grid: { left: 40, right: 40, bottom: 30, top: 40, containLabel: true },
    xAxis: { type: "category", boundaryGap: false, data: dates },
    yAxis: { type: "value" },
    series: [
      { name: "浏览", type: "line", smooth: true, data: views, lineStyle: { width: 3, color: "#74b9ff" } },
      { name: "加购", type: "line", smooth: true, data: carts, lineStyle: { width: 3, color: "#fd79a8" } },
      { name: "购买", type: "line", smooth: true, data: buys, lineStyle: { width: 4, color: "#55efc4" } },
    ],
  });
}

onMounted(async () => {
  loading.value = true;
  try {
    const res = await request.get("/admin/stats");
    stats.value = res.data;
    nextTick(() => {
      initAlgoChart();
      initCategoryChart();
      initTrendChart();
    });
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
}
.sc-icon { font-size: 36px; }
.sc-num { font-size: 28px; font-weight: 800; color: var(--primary); }
.sc-label { font-size: 13px; color: var(--text-muted); }

/* ── 图表 ── */
.charts-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}
.chart-full { grid-column: span 2; }
.chart-container {
  height: 300px;
  width: 100%;
}
.trend-chart { height: 350px; }

/* ── 区块 ── */
.section-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
}
.section-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 18px;
  color: #333;
}

/* ── 快捷入口 ── */
.quick-grid { display: flex; gap: 12px; }
.quick-item {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 20px 32px; border: 1px solid var(--border); border-radius: var(--radius-md);
  cursor: pointer; font-size: 13px; color: var(--text-secondary); transition: all 0.3s;
}
.quick-item span:first-child { font-size: 28px; }
.quick-item:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-bg); }
</style>

