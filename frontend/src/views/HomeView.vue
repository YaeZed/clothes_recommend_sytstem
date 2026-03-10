<template>
  <div class="home-page">
    <!-- 淘宝风格首屏 3列布局 -->
    <section class="tb-first-screen">
      <!-- 左侧：垂直类目菜单 -->
      <div class="tb-category-menu">
        <h3>全部分类</h3>
        <ul>
          <li v-for="cat in quickCats" :key="cat.label" @click="goCat(cat.cat)">
            <span class="cat-icon">{{ cat.icon }}</span>
            <span class="cat-name">{{ cat.label }}</span>
            <el-icon class="cat-arrow"><ArrowRight /></el-icon>
          </li>
        </ul>
      </div>

      <!-- 中间：大图轮播 -->
      <div class="tb-banner">
        <el-carousel height="380px" :interval="4000" arrow="hover">
          <el-carousel-item v-for="(b, i) in banners" :key="i">
            <div
              class="banner-slide"
              :style="{ background: b.bg }"
              @click="$router.push(b.link)"
            >
              <div class="banner-content">
                <div class="banner-badge">{{ b.badge }}</div>
                <h2 class="banner-title">{{ b.title }}</h2>
                <p class="banner-desc">{{ b.desc }}</p>
                <div class="banner-btn">{{ b.btnText }}</div>
              </div>
              <div class="banner-emoji">{{ b.emoji }}</div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>

      <!-- 右侧：用户面板 -->
      <div class="tb-user-panel">
        <div class="user-info" v-if="auth.isLoggedIn">
          <el-avatar
            :size="50"
            style="background: #ff5000; color: #fff; font-size: 24px"
          >
            {{ auth.user?.username?.[0]?.toUpperCase() }}
          </el-avatar>
          <div class="greeting">Hi! {{ auth.user?.username }}</div>
          <div class="user-level">
            <el-tag size="small" type="danger" effect="dark">钻石会员</el-tag>
          </div>
          <div class="user-actions">
            <div class="u-act" @click="$router.push('/profile?tab=favorites')">
              <strong>{{ favs.loaded ? "12" : "-" }}</strong>
              <span>收藏夹</span>
            </div>
            <div class="u-act" @click="$router.push('/profile?tab=history')">
              <strong>18</strong>
              <span>历史浏览</span>
            </div>
            <div class="u-act" @click="$router.push('/profile')">
              <strong>2</strong>
              <span>待收货</span>
            </div>
          </div>
        </div>
        <div class="user-info not-logged" v-else>
          <el-avatar :size="50" icon="UserFilled" />
          <div class="greeting">Hi! 欢迎来到淘宝</div>
          <div class="auth-btns">
            <el-button
              type="primary"
              round
              @click="$router.push('/auth/login')"
              style="width: 100px"
              >登录</el-button
            >
            <el-button
              round
              @click="$router.push('/auth/register')"
              style="width: 100px"
              >注册</el-button
            >
          </div>
        </div>

        <div class="tb-notices">
          <div class="notice-head">
            <h4>公告</h4>
          </div>
          <ul class="notice-list">
            <li>
              <el-tag size="small" type="danger">特惠</el-tag> 春夏穿搭指南上线
            </li>
            <li>
              <el-tag size="small" type="danger">热议</el-tag>
              DeepFM算法推荐揭秘
            </li>
            <li>
              <el-tag size="small" type="warning">上新</el-tag> 2026早秋风衣大赏
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 猜你喜欢 (类似于淘宝首页下方的瀑布流) -->
    <section class="tb-guess-you-like">
      <div class="section-title">
        <h2>✨ 猜你喜欢 <span class="ai-badge">AI 专属推荐</span></h2>
      </div>

      <!-- AI 个性化推荐 (如果登录) -->
      <div v-if="auth.isLoggedIn">
        <div class="rec-badge" v-if="personalData.coldStart">
          <el-icon><MagicStick /></el-icon> AI推荐计算中，先看看大家都在买什么
        </div>
        <ProductGrid
          :products="personalData.items"
          :loading="loadingPersonal"
          :skeleton-count="20"
        />
      </div>

      <!-- 未登录显示热门 -->
      <div v-else>
        <ProductGrid
          :products="hotProducts"
          :loading="loadingHot"
          :skeleton-count="20"
        />
      </div>
    </section>

    <!-- 冷启动：风格测试弹窗 -->
    <el-dialog
      v-model="showStyleTest"
      title="✨ 欢迎来到淘宝！选择偏好开启个性推荐"
      width="600px"
      :close-on-click-modal="false"
      :show-close="false"
      class="style-test-dialog"
    >
      <p class="st-desc">
        我们注意到你是新朋友，请选择 1~3
        个你喜欢的穿搭风格，我们会为你定制专属首页商品。
      </p>

      <div class="st-grid">
        <div
          v-for="s in allStyles"
          :key="s.name"
          class="st-card"
          :class="{ active: selectedStyles.includes(s.name) }"
          @click="toggleStyle(s.name)"
        >
          <div class="st-emoji">{{ s.emoji }}</div>
          <div class="st-name">{{ s.name }}</div>
          <div class="st-check" v-if="selectedStyles.includes(s.name)">✓</div>
        </div>
      </div>

      <template #footer>
        <el-button
          type="primary"
          round
          :loading="savingStyle"
          :disabled="selectedStyles.length === 0"
          @click="submitStyleTest"
        >
          开启专属推荐 (已选 {{ selectedStyles.length }})
        </el-button>
        <el-button text @click="skipStyleTest">跳过测试，随便看看</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import { useFavStore } from "../store/favorites";
import { getHotRecommend, getPersonalRecommend } from "../api/recommend";
import ProductGrid from "../components/ProductGrid.vue";
import { ArrowRight, MagicStick } from "@element-plus/icons-vue";
import { updateProfile } from "../api/auth";
import { ElMessage } from "element-plus";

const auth = useAuthStore();
const favs = useFavStore();
const router = useRouter();

const hotProducts = ref([]);
const personalData = ref({ items: [], coldStart: false });
const loadingHot = ref(false);
const loadingPersonal = ref(false);

// 冷启动相关
const showStyleTest = ref(false);
const selectedStyles = ref([]);
const savingStyle = ref(false);
const allStyles = [
  { name: "休闲", emoji: "☕" },
  { name: "正式", emoji: "👔" },
  { name: "运动", emoji: "🏀" },
  { name: "街头", emoji: "🛹" },
  { name: "复古", emoji: "📻" },
  { name: "简约", emoji: "🍃" },
  { name: "时尚", emoji: "✨" },
  { name: "森系", emoji: "🌲" },
  { name: "潮流", emoji: "🔥" },
];

function toggleStyle(name) {
  const idx = selectedStyles.value.indexOf(name);
  if (idx > -1) {
    selectedStyles.value.splice(idx, 1);
  } else {
    if (selectedStyles.value.length >= 3) {
      ElMessage.warning("最多选择 3 个风格哦");
      return;
    }
    selectedStyles.value.push(name);
  }
}

async function submitStyleTest() {
  savingStyle.value = true;
  try {
    await updateProfile({
      stylePref: selectedStyles.value,
      sizeInfo: auth.user?.sizeInfo || {},
    });
    await auth.fetchProfile();
    ElMessage.success("设置成功，正在为你生成个性化推荐！");
    showStyleTest.value = false;

    loadingPersonal.value = true;
    const res2 = await getPersonalRecommend(20);
    personalData.value = res2.data;
    loadingPersonal.value = false;
  } finally {
    savingStyle.value = false;
  }
}

function skipStyleTest() {
  showStyleTest.value = false;
}

const banners = [
  {
    bg: "linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&q=80&w=1200') center/cover",
    badge: "🔥 新品上市",
    title: "2026 秋冬季新款大赏",
    desc: "精选百款热门单品，限时直降",
    link: "/products",
    btnText: "立即抢购",
    emoji: "👗",
  },
  {
    bg: "linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&q=80&w=1200') center/cover",
    badge: "🤖 AI 精选",
    title: "专属穿搭推荐",
    desc: "基于 DeepFM + 协同过滤算法，为你量身定制",
    link: "/products",
    btnText: "查看推荐",
    emoji: "✨",
  },
  {
    bg: "linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.2)), url('https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&q=80&w=1200') center/cover",
    badge: "🌿 清凉限定",
    title: "夏日清爽穿搭",
    desc: "轻盈面料 · 多款配色，清凉一夏",
    link: "/products?category=上衣",
    btnText: "探索穿搭",
    emoji: "🌸",
  },
];

const sideCards = [
  { icon: "🏆", label: "排行榜", sub: "热销TOP100", action: "hot" },
  { icon: "⭐", label: "我的收藏", sub: "查看收藏商品", action: "fav" },
  { icon: "🧾", label: "购买记录", sub: "历史交互记录", action: "history" },
  { icon: "🎁", label: "猜你喜欢", sub: "专属个性推荐", action: "personal" },
];

const quickCats = [
  { icon: "👕", label: "上衣", cat: "上衣" },
  { icon: "👖", label: "裤子", cat: "裤子" },
  { icon: "👒", label: "配饰", cat: "配饰" },
  { icon: "🧣", label: "卫衣", cat: "卫衣" },
  { icon: "🧥", label: "外套", cat: "外套" },
  { icon: "👟", label: "鞋子", cat: "鞋子" },
  { icon: "👗", label: "裙子", cat: "裙子" },
];

function goCat(cat) {
  router.push({ path: "/products", query: { category: cat } });
}

function sideClick(s) {
  if (s.action === "hot") router.push("/products?sortBy=sales_count");
  else if (s.action === "personal") router.push("/products");
  else if (auth.isLoggedIn)
    router.push(
      "/profile?tab=" + (s.action === "fav" ? "favorites" : "history"),
    );
  else router.push("/auth/login");
}

onMounted(async () => {
  loadingHot.value = true;
  const res = await getHotRecommend(20);
  hotProducts.value = res.data.items;
  loadingHot.value = false;

  if (auth.isLoggedIn) {
    if (!auth.user?.stylePref || auth.user.stylePref.length === 0) {
      showStyleTest.value = true;
    }

    loadingPersonal.value = true;
    const res2 = await getPersonalRecommend(20);
    personalData.value = res2.data;
    loadingPersonal.value = false;
  }
});
</script>

<style scoped>
/* ── 冷启动弹窗 ── */
.st-desc {
  color: var(--text-regular);
  margin-bottom: 20px;
  line-height: 1.6;
}
.st-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.st-card {
  background: #f5f7fa;
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  padding: 24px 16px;
  text-align: center;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}
.st-card:hover {
  background: #fff;
  border-color: #ffb880;
  box-shadow: 0 4px 12px rgba(255, 80, 0, 0.1);
}
.st-card.active {
  background: #fff5eb;
  border-color: var(--primary);
}
.st-emoji {
  font-size: 32px;
  margin-bottom: 8px;
}
.st-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.st-check {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: var(--primary);
  color: #fff;
  border-radius: 50%;
  line-height: 24px;
  text-align: center;
  font-weight: bold;
  font-size: 14px;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.home-page {
  padding-top: 10px;
}

/* ── 淘宝风格首屏 3列布局 ── */
.tb-first-screen {
  display: flex;
  gap: 12px;
  height: 380px;
  margin-bottom: 30px;
}

/* 左侧分类 */
.tb-category-menu {
  width: 220px;
  background: #fff;
  border-radius: 12px;
  padding: 16px 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}
.tb-category-menu h3 {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  padding: 0 16px 12px;
  margin: 0;
}
.tb-category-menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.tb-category-menu li {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
  color: #666;
  font-size: 14px;
}
.tb-category-menu li:hover {
  background: #ffe6e0;
  color: #ff5000;
}
.cat-icon {
  margin-right: 12px;
  font-size: 18px;
}
.cat-name {
  flex: 1;
}
.cat-arrow {
  color: #ccc;
  font-size: 12px;
}

/* 中间轮播 */
.tb-banner {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}
.banner-slide {
  height: 100%;
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  cursor: pointer;
}
.banner-content {
  z-index: 2;
  color: #fff;
}
.banner-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.3);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin-bottom: 12px;
  backdrop-filter: blur(4px);
}
.banner-title {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
.banner-desc {
  font-size: 15px;
  opacity: 0.9;
  margin-bottom: 24px;
}
.banner-btn {
  display: inline-block;
  background: #fff;
  color: #ff5000;
  padding: 8px 24px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 14px;
}
.banner-emoji {
  position: absolute;
  right: 40px;
  font-size: 160px;
  opacity: 0.2;
  top: 50%;
  transform: translateY(-50%);
  user-select: none;
}

/* 右侧用户面板 */
.tb-user-panel {
  width: 250px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.user-info {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  height: 190px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.not-logged {
  justify-content: center;
}
.greeting {
  font-weight: 700;
  font-size: 14px;
  margin: 8px 0;
}
.user-level {
  margin-bottom: 12px;
}
.user-actions {
  display: flex;
  width: 100%;
  justify-content: space-around;
  margin-top: auto;
}
.u-act {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}
.u-act strong {
  font-size: 16px;
  color: #333;
}
.u-act span {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
.u-act:hover span {
  color: #ff5000;
}
.auth-btns {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.tb-notices {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  flex: 1;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}
.notice-head h4 {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 12px;
  color: #333;
}
.notice-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.notice-list li {
  font-size: 13px;
  color: #555;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.notice-list li:hover {
  color: #ff5000;
}

/* ── 猜你喜欢 ── */
.tb-guess-you-like {
  padding-bottom: 40px;
}
.section-title {
  text-align: center;
  margin-bottom: 24px;
  padding-top: 10px;
}
.section-title h2 {
  font-size: 24px;
  font-weight: 800;
  color: #ff5000;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.ai-badge {
  font-size: 13px;
  background: linear-gradient(135deg, #ff4400, #ff8800);
  color: #fff;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: normal;
  vertical-align: middle;
}
.rec-badge {
  text-align: center;
  background: #fff3e8;
  color: #ff5000;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
</style>
