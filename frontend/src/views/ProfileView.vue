<template>
  <div class="profile-page">
    <!-- 顶部用户信息横幅 -->
    <div class="profile-banner">
      <el-avatar
        :size="72"
        class="banner-avatar hoverable"
        :src="auth.user?.avatar"
        @click="$refs.avatarInput.click()"
      >
        {{ auth.user?.username?.[0]?.toUpperCase() }}
      </el-avatar>
      <input
        type="file"
        ref="avatarInput"
        style="display: none"
        accept="image/*"
        @change="onAvatarChange"
      />
      <div class="banner-info">
        <div class="banner-username">
          {{ auth.user?.nickname || auth.user?.username }}
          <el-tag
            v-if="auth.isAdmin"
            type="danger"
            size="small"
            style="margin-left: 8px"
            >管理员</el-tag
          >
          <el-tag v-else type="danger" size="small" style="margin-left: 8px"
            >钻石会员</el-tag
          >
        </div>
        <div class="banner-stats">
          <div class="stat-item">
            <strong>{{ stats.total || 0 }}</strong
            ><span>互动</span>
          </div>
          <div class="stat-item">
            <strong>{{ stats.collect || 0 }}</strong
            ><span>收藏</span>
          </div>
          <div class="stat-item">
            <strong>{{ stats.purchase || 0 }}</strong
            ><span>购买</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 区域 -->
    <el-tabs v-model="activeTab" class="profile-tabs" @tab-click="onTabClick">
      <!-- ─── 我的信息 ─── -->
      <el-tab-pane label="我的信息" name="info">
        <div class="tab-body">
          <div class="section-title">基本信息</div>
          <el-form :model="form" label-width="80px" class="basic-info-form">
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" placeholder="输入您的昵称" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="form.phone" placeholder="输入手机号" />
            </el-form-item>
            <el-form-item label="生日">
              <el-date-picker
                v-model="form.birthday"
                type="date"
                placeholder="选择生日"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>

          <el-divider />
          <div class="section-title">风格偏好</div>
          <el-checkbox-group v-model="form.stylePref" class="style-checks">
            <el-checkbox-button v-for="s in allStyles" :key="s" :label="s">{{
              s
            }}</el-checkbox-button>
          </el-checkbox-group>

          <el-divider />
          <div class="section-title">身体数据</div>
          <div class="size-row">
            <el-form-item label="身高(cm)">
              <el-input-number
                v-model="form.sizeInfo.height"
                :min="140"
                :max="220"
              />
            </el-form-item>
            <el-form-item label="体重(kg)">
              <el-input-number
                v-model="form.sizeInfo.weight"
                :min="30"
                :max="150"
              />
            </el-form-item>
          </div>

          <el-divider />
          <div class="section-title">收货地址</div>
          <div class="address-list">
            <div
              class="address-item"
              v-for="(addr, idx) in form.addresses"
              :key="idx"
            >
              <div class="addr-info">
                <strong>{{ addr.name }}</strong> {{ addr.phone }}
                <el-tag
                  size="small"
                  type="danger"
                  v-if="addr.isDefault"
                  style="margin-left: 8px"
                  >默认</el-tag
                >
                <div class="addr-detail">{{ addr.address }}</div>
              </div>
              <div class="addr-actions">
                <el-button type="primary" link @click="editAddress(idx)"
                  >编辑</el-button
                >
                <el-button type="danger" link @click="delAddress(idx)"
                  >删除</el-button
                >
              </div>
            </div>
            <el-button
              plain
              icon="Plus"
              @click="addAddress"
              style="margin-top: 12px; width: 100%"
              >新增收货地址</el-button
            >
          </div>

          <div class="form-actions">
            <el-button
              type="primary"
              class="save-btn"
              :loading="saving"
              @click="saveProfile"
            >
              保存修改
            </el-button>
            <el-button class="pw-btn" @click="pwDialog.visible = true"
              >修改密码</el-button
            >
          </div>
        </div>
      </el-tab-pane>

      <!-- ─── 我的收藏 ─── -->
      <el-tab-pane label="我的收藏" name="favorites">
        <div class="tab-body">
          <ProductGrid
            :products="favorites"
            :loading="loadingFav"
            :skeleton-count="10"
            empty-text="还没有收藏的商品哦～"
          />
          <div class="load-more" v-if="favTotal > favorites.length">
            <el-button @click="loadMoreFav" :loading="loadingMoreFav"
              >加载更多</el-button
            >
          </div>
        </div>
      </el-tab-pane>

      <!-- ─── 浏览历史 ─── -->
      <el-tab-pane label="浏览历史" name="history">
        <div class="tab-body">
          <div class="history-list" v-if="!loadingHistory">
            <div
              v-for="item in history"
              :key="item.id"
              class="history-row"
              @click="$router.push(`/products/${item.productId}`)"
            >
              <img
                :src="
                  item.product?.images?.[0] ||
                  'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'100%25\' height=\'100%25\'%3E%3Crect width=\'100%25\' height=\'100%25\' fill=\'%23eeeeee\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' fill=\'%23999999\' font-family=\'sans-serif\' font-size=\'14\' text-anchor=\'middle\' dominant-baseline=\'middle\'%3ENo Image%3C/text%3E%3C/svg%3E'
                "
                class="history-img"
                @error="
                  $event.target.src =
                    'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'100%25\' height=\'100%25\'%3E%3Crect width=\'100%25\' height=\'100%25\' fill=\'%23eeeeee\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' fill=\'%23999999\' font-family=\'sans-serif\' font-size=\'14\' text-anchor=\'middle\' dominant-baseline=\'middle\'%3ENo Image%3C/text%3E%3C/svg%3E'
                "
              />
              <div class="history-info">
                <div class="history-title">
                  {{ item.product?.title || "商品已下架" }}
                </div>
                <div class="history-meta">
                  <el-tag size="small" v-if="item.product?.category">{{
                    item.product.category
                  }}</el-tag>
                  <el-tag
                    size="small"
                    type="success"
                    v-if="item.product?.style"
                    >{{ item.product.style }}</el-tag
                  >
                  <span class="history-action">{{
                    ACTION_LABELS[item.actionType]
                  }}</span>
                </div>
                <div class="history-price" v-if="item.product?.price">
                  ¥{{ Number(item.product.price).toFixed(2) }}
                </div>
              </div>
              <div class="history-time">{{ fmtTime(item.createdAt) }}</div>
            </div>
            <div v-if="!history.length" class="empty-hint">暂无浏览历史</div>
          </div>
          <el-skeleton v-else :rows="4" animated />
          <div
            class="load-more"
            v-if="histTotal > history.length && !loadingHistory"
          >
            <el-button @click="loadMoreHist" :loading="loadingMoreHist"
              >加载更多</el-button
            >
          </div>
        </div>
      </el-tab-pane>

      <!-- ─── 我的订单 ─── -->
      <el-tab-pane label="我的订单" name="orders">
        <div class="tab-body">
          <div class="orders-list" v-if="!loadingOrders">
            <div v-for="order in orders" :key="order.id" class="order-card">
              <div class="order-head">
                <span class="order-no">订单号: {{ order.orderNo }}</span>
                <span class="order-status" :class="order.status">{{
                  orderStatusText[order.status] || order.status
                }}</span>
              </div>
              <div class="order-items">
                <div
                  v-for="item in order.items"
                  :key="item.id"
                  class="o-item"
                  @click="$router.push(`/products/${item.productId}`)"
                >
                  <img
                    :src="
                      item.productImage ||
                      'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'100%25\' height=\'100%25\'%3E%3Crect width=\'100%25\' height=\'100%25\' fill=\'%23eeeeee\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' fill=\'%23999999\' font-family=\'sans-serif\' font-size=\'14\' text-anchor=\'middle\' dominant-baseline=\'middle\'%3ENo Image%3C/text%3E%3C/svg%3E'
                    "
                    class="o-img"
                  />
                  <div class="o-info">
                    <div class="o-title">{{ item.productTitle }}</div>
                    <div class="o-meta">
                      <el-tag
                        size="small"
                        v-if="item.attributes?.color"
                        style="margin-right: 4px"
                        >{{ item.attributes.color }}</el-tag
                      >
                      <el-tag
                        size="small"
                        v-if="item.attributes?.size"
                        type="info"
                        >{{ item.attributes.size }}</el-tag
                      >
                    </div>
                  </div>
                  <div class="o-price-qty">
                    <div class="o-price">
                      ¥{{ Number(item.price).toFixed(2) }}
                    </div>
                    <div class="o-qty">x{{ item.quantity }}</div>
                  </div>
                </div>
              </div>
              <div class="order-foot">
                <span class="o-time">{{ fmtTime(order.createdAt) }}</span>
                <div class="o-addr" v-if="order.receiver">
                  <el-icon><Location /></el-icon>
                  {{ order.receiver.name }} {{ order.receiver.phone }} | {{ order.receiver.address }}
                </div>
                <span class="o-total"
                  >实付款:
                  <strong
                    >¥{{ Number(order.totalAmount).toFixed(2) }}</strong
                  ></span
                >
              </div>
            </div>
            <div v-if="!orders.length" class="empty-hint">暂无订单记录</div>
          </div>
          <el-skeleton v-else :rows="4" animated />
        </div>
      </el-tab-pane>
      <!-- ─── 我的画像 ─── -->
      <el-tab-pane label="我的画像" name="portrait">
        <div class="tab-body" v-if="portrait">
          <!-- 行为统计 -->
          <div class="section-title">行为统计</div>
          <div class="behavior-stat-row">
            <div
              class="bstat-card"
              v-for="(item, key) in behaviorDisplayStats"
              :key="key"
            >
              <div class="bstat-num">
                {{ portrait.behaviorStats?.[key] || 0 }}
              </div>
              <div class="bstat-label">{{ item.label }}</div>
              <div class="bstat-icon">{{ item.icon }}</div>
            </div>
          </div>

          <!-- 品类偏好 -->
          <el-divider />
          <div class="section-title">品类兴趣偏好（基于行为加权）</div>
          <div class="category-bars">
            <div
              v-for="item in portrait.categoryPref"
              :key="item.category"
              class="cat-bar-row"
            >
              <span class="cat-bar-label">{{ item.category }}</span>
              <div class="cat-bar-track">
                <div
                  class="cat-bar-fill"
                  :style="{
                    width: catBarWidth(item.score) + '%',
                  }"
                />
              </div>
              <span class="cat-bar-score">{{ item.score }}</span>
            </div>
            <div v-if="!portrait.categoryPref?.length" class="empty-hint">
              暂无足够行为数据，多浏览商品后会自动更新～
            </div>
          </div>

          <!-- 风格标签 -->
          <el-divider />
          <div class="section-title">风格偏好标签</div>
          <div class="style-tag-area">
            <el-tag
              v-for="s in portrait.stylePref"
              :key="s"
              type="warning"
              size="large"
              style="margin: 4px"
              >{{ s }}</el-tag
            >
            <span v-if="!portrait.stylePref?.length" class="empty-hint"
              >尚未设置，前往「我的信息」添加偏好风格</span
            >
          </div>

          <!-- 近7天活跃度 -->
          <el-divider />
          <div class="section-title">近7日行为活跃度</div>
          <div class="weekly-bars">
            <div
              v-for="day in portrait.weeklyActivity"
              :key="day.date"
              class="week-col"
            >
              <div class="week-bar-wrap">
                <div
                  class="week-bar-fill"
                  :style="{ height: weekBarHeight(day.count) + '%' }"
                />
              </div>
              <div class="week-label">{{ day.date.slice(5) }}</div>
              <div class="week-count">{{ day.count }}</div>
            </div>
          </div>
        </div>
        <el-skeleton v-else :rows="5" animated style="padding: 20px" />
      </el-tab-pane>
    </el-tabs>

    <!-- 地址编辑弹窗 -->
    <el-dialog
      v-model="addrDialog.visible"
      :title="addrDialog.isEdit ? '编辑地址' : '新增地址'"
      width="400px"
    >
      <el-form :model="addrDialog.form" label-width="80px">
        <el-form-item label="收件人">
          <el-input v-model="addrDialog.form.name" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="addrDialog.form.phone" />
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input
            v-model="addrDialog.form.address"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="addrDialog.form.isDefault" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addrDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveAddress">保存</el-button>
      </template>
    </el-dialog>
    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwDialog.visible" title="修改密码" width="400px">
      <el-form :model="pwDialog.form" label-width="80px">
        <el-form-item label="原密码">
          <el-input
            v-model="pwDialog.form.oldPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="pwDialog.form.newPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="pwDialog.form.confirmPassword"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwDialog.visible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="pwDialog.saving"
          @click="savePassword"
          >保存</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import { updateProfile, updatePassword } from "../api/auth";
import {
  getFavorites,
  getBehaviorHistory,
  getBehaviorStats,
  getUserPortrait,
} from "../api/behavior";
import { getOrders } from "../api/order";
import { ElMessage } from "element-plus";
import ProductGrid from "../components/ProductGrid.vue";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const allStyles = [
  "休闲",
  "正式",
  "运动",
  "街头",
  "复古",
  "简约",
  "时尚",
  "森系",
  "潮流",
];

const ACTION_LABELS = {
  view: "👀 浏览",
  collect: "⭐ 收藏",
  cart: "🛒 加购",
  purchase: "✅ 购买",
};

const activeTab = ref(route.query.tab || "info");
const saving = ref(false);
const stats = ref({});

const form = reactive({
  nickname: auth.user?.nickname || "",
  phone: auth.user?.phone || "",
  birthday: auth.user?.birthday || "",
  stylePref: [...(auth.user?.stylePref || [])],
  sizeInfo: {
    height: auth.user?.sizeInfo?.height || 168,
    weight: auth.user?.sizeInfo?.weight || 55,
  },
  addresses: [...(auth.user?.addresses || [])],
});

// 头像上传
async function onAvatarChange(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async (ev) => {
    const base64 = ev.target.result;
    try {
      saving.value = true;
      await updateProfile({ avatar: base64 });
      await auth.fetchProfile();
      ElMessage.success("头像更新成功");
    } finally {
      saving.value = false;
    }
  };
  reader.readAsDataURL(file);
}

// 地址管理
const addrDialog = reactive({
  visible: false,
  isEdit: false,
  editIdx: -1,
  form: { name: "", phone: "", address: "", isDefault: false },
});

function addAddress() {
  addrDialog.isEdit = false;
  addrDialog.form = {
    name: "",
    phone: "",
    address: "",
    isDefault: form.addresses.length === 0,
  };
  addrDialog.visible = true;
}

function editAddress(idx) {
  addrDialog.isEdit = true;
  addrDialog.editIdx = idx;
  addrDialog.form = { ...form.addresses[idx] };
  addrDialog.visible = true;
}

function delAddress(idx) {
  form.addresses.splice(idx, 1);
  saveProfile(); // 直接保存
}

function saveAddress() {
  if (
    !addrDialog.form.name ||
    !addrDialog.form.phone ||
    !addrDialog.form.address
  ) {
    ElMessage.warning("请完善地址信息");
    return;
  }

  if (addrDialog.form.isDefault) {
    // Other addresses become not default
    form.addresses.forEach((a) => (a.isDefault = false));
  }

  if (addrDialog.isEdit) {
    form.addresses[addrDialog.editIdx] = { ...addrDialog.form };
  } else {
    addrDialog.form.id = Date.now();
    form.addresses.push({ ...addrDialog.form });
  }
  addrDialog.visible = false;
  saveProfile(); // 直接保存
}

const pwDialog = reactive({
  visible: false,
  saving: false,
  form: { oldPassword: "", newPassword: "", confirmPassword: "" },
});

async function savePassword() {
  if (!pwDialog.form.oldPassword || !pwDialog.form.newPassword) {
    ElMessage.warning("密码不能为空");
    return;
  }
  if (pwDialog.form.newPassword !== pwDialog.form.confirmPassword) {
    ElMessage.warning("两次输入的新密码不一致");
    return;
  }
  pwDialog.saving = true;
  try {
    await updatePassword({
      oldPassword: pwDialog.form.oldPassword,
      newPassword: pwDialog.form.newPassword,
    });
    ElMessage.success("密码修改成功，请重新登录");
    pwDialog.visible = false;
    auth.logout();
    router.push("/login");
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || "修改失败");
  } finally {
    pwDialog.saving = false;
    pwDialog.form = { oldPassword: "", newPassword: "", confirmPassword: "" };
  }
}

// 收藏
const favorites = ref([]);
const favTotal = ref(0);
const favPage = ref(1);
const loadingFav = ref(false);
const loadingMoreFav = ref(false);

// 历史
const history = ref([]);
const histTotal = ref(0);
const histPage = ref(1);
const loadingHistory = ref(false);
const loadingMoreHist = ref(false);

// 订单
const orders = ref([]);
const loadingOrders = ref(false);
const orderStatusText = {
  pending: "待支付",
  paid: "已支付",
  shipped: "已发货",
  completed: "已完成",
  cancelled: "已取消",
};

async function loadOrders() {
  loadingOrders.value = true;
  try {
    const res = await getOrders();
    orders.value = res.data || [];
  } finally {
    loadingOrders.value = false;
  }
}

// 画像
const portrait = ref(null);
const behaviorDisplayStats = {
  view: { label: "浏览频次", icon: "👀" },
  collect: { label: "收藏意向", icon: "⭐" },
  cart: { label: "加购意向", icon: "🛒" },
  purchase: { label: "购买转化", icon: "🎁" },
};

const maxCatScore = computed(() => {
  if (!portrait.value?.categoryPref?.length) return 1;
  return Math.max(...portrait.value.categoryPref.map((c) => c.score));
});
function catBarWidth(score) {
  return (score / maxCatScore.value) * 100;
}

const maxWeekCnt = computed(() => {
  if (!portrait.value?.weeklyActivity?.length) return 1;
  return Math.max(...portrait.value.weeklyActivity.map((d) => d.count));
});
function weekBarHeight(count) {
  if (maxWeekCnt.value === 0) return 0;
  return Math.max((count / maxWeekCnt.value) * 100, 2); // 至少给2%高度意思一下
}

async function loadPortrait() {
  try {
    const res = await getUserPortrait();
    portrait.value = res.data;
  } catch (_) {}
}

async function saveProfile() {
  saving.value = true;
  try {
    await updateProfile(form);
    await auth.fetchProfile();
    ElMessage.success("保存成功");
  } finally {
    saving.value = false;
  }
}

async function loadFavorites(reset = false) {
  if (reset) {
    favorites.value = [];
    favPage.value = 1;
  }
  const loading = reset ? loadingFav : loadingMoreFav;
  loading.value = true;
  try {
    const res = await getFavorites({ page: favPage.value, perPage: 20 });
    favorites.value.push(...(res.data?.items || []));
    favTotal.value = res.data?.total || 0;
    favPage.value++;
  } finally {
    loading.value = false;
  }
}

async function loadMoreFav() {
  loadingMoreFav.value = true;
  await loadFavorites(false);
}

async function loadHistory(reset = false) {
  if (reset) {
    history.value = [];
    histPage.value = 1;
  }
  const loading = reset ? loadingHistory : loadingMoreHist;
  loading.value = true;
  try {
    const res = await getBehaviorHistory({ page: histPage.value, perPage: 20 });
    history.value.push(...(res.data?.items || []));
    histTotal.value = res.data?.total || 0;
    histPage.value++;
  } finally {
    loading.value = false;
  }
}

async function loadMoreHist() {
  loadingMoreHist.value = true;
  await loadHistory(false);
}

function onTabClick({ paneName }) {
  if (paneName === "favorites" && favorites.value.length === 0)
    loadFavorites(true);
  if (paneName === "history" && history.value.length === 0) loadHistory(true);
  if (paneName === "orders" && orders.value.length === 0) loadOrders();
  if (paneName === "portrait" && !portrait.value) loadPortrait();
}

function fmtTime(t) {
  if (!t) return "";
  const d = new Date(t);
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

onMounted(async () => {
  // 加载行为统计
  try {
    const sRes = await getBehaviorStats();
    stats.value = sRes.data || {};
  } catch (_) {}

  // 根据 URL query 参数决定初始加载哪个 tab
  if (activeTab.value === "favorites") loadFavorites(true);
  else if (activeTab.value === "history") loadHistory(true);
  else if (activeTab.value === "orders") loadOrders();
  else if (activeTab.value === "portrait") loadPortrait();
});
</script>

<style scoped>
/* ── 订单 ── */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.order-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.order-head {
  padding: 12px 16px;
  background: #fafafa;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
  font-size: 13px;
  color: #666;
}
.order-status {
  font-weight: bold;
}
.order-status.paid {
  color: #67c23a;
}
.order-status.pending {
  color: #e6a23c;
}
.order-status.shipped {
  color: #409eff;
}

.order-items {
  padding: 12px 16px;
}
.o-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px dashed #eee;
  cursor: pointer;
  transition: background 0.2s;
}
.o-item:last-child {
  border-bottom: none;
}
.o-item:hover {
  background: #fdfdfd;
}
.o-img {
  width: 60px;
  height: 72px;
  object-fit: cover;
  border-radius: 4px;
}
.o-info {
  flex: 1;
  min-width: 0;
}
.o-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.o-meta {
  font-size: 12px;
}
.o-price-qty {
  text-align: right;
  flex-shrink: 0;
}
.o-price {
  font-weight: bold;
  color: #333;
  font-size: 14px;
}
.o-qty {
  color: #999;
  font-size: 13px;
  margin-top: 4px;
}
.order-foot {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eee;
  font-size: 13px;
  color: #666;
}
.o-addr {
  flex: 1;
  margin: 0 20px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  gap: 4px;
}
.o-addr .el-icon {
  font-size: 14px;
  color: #999;
}
.o-total strong {
  font-size: 18px;
  color: var(--primary);
  margin-left: 4px;
}

/* ── Banner ── */
.profile-page {
  max-width: 900px;
  margin: 0 auto;
}

.profile-banner {
  background: linear-gradient(135deg, var(--primary) 0%, #ff8c00 100%);
  border-radius: var(--radius-lg);
  padding: 28px 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 20px rgba(255, 80, 0, 0.15);
}
.banner-avatar {
  background: rgba(255, 255, 255, 0.3) !important;
  color: #fff !important;
  font-size: 30px;
  font-weight: 800;
  flex-shrink: 0;
}
.banner-info {
  flex: 1;
}
.banner-username {
  font-size: 22px;
  font-weight: 800;
  color: #fff;
  margin-bottom: 12px;
}
.banner-stats {
  display: flex;
  gap: 28px;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat-item strong {
  font-size: 22px;
  font-weight: 800;
  color: #fff;
}
.stat-item span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

/* ── Tabs ── */
.profile-tabs {
  background: #fff;
  border-radius: var(--radius-lg);
  overflow: hidden;
}
:deep(.el-tabs__header) {
  padding: 0 20px;
  border-bottom: 1px solid var(--border);
}
:deep(.el-tabs__item.is-active) {
  color: var(--primary);
}
:deep(.el-tabs__active-bar) {
  background: var(--primary);
}

.tab-body {
  padding: 24px;
}

/* 信息 tab */
.section-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 14px;
  color: var(--text-primary);
}
.style-checks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 4px;
}
.size-row {
  display: flex;
  gap: 32px;
}
.form-actions {
  margin-top: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}
.save-btn {
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  font-weight: 600 !important;
  padding: 0 40px !important;
  height: 40px !important;
}
.pw-btn {
  height: 40px !important;
}

/* 历史 tab */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.history-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: var(--radius-md);
  background: #fafafa;
  cursor: pointer;
  transition: box-shadow var(--transition);
}
.history-row:hover {
  box-shadow: var(--shadow-md);
  background: #fff;
}
.history-img {
  width: 72px;
  height: 90px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
  background: #eee;
}
.history-info {
  flex: 1;
  min-width: 0;
}
.history-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.history-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.history-action {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}
.history-price {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary);
}
.history-time {
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.empty-hint {
  text-align: center;
  color: var(--text-muted);
  padding: 40px;
}
.load-more {
  text-align: center;
  padding: 20px 0;
}

/* ── 画像 tab ── */
.behavior-stat-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}
.bstat-card {
  flex: 1;
  background: #f8f9fa;
  border-radius: var(--radius-md);
  padding: 16px;
  text-align: center;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border);
  transition: transform var(--transition);
}
.bstat-card:hover {
  transform: translateY(-2px);
  border-color: var(--primary);
}
.bstat-num {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.bstat-label {
  font-size: 13px;
  color: var(--text-muted);
}
.bstat-icon {
  position: absolute;
  right: -10px;
  bottom: -15px;
  font-size: 60px;
  opacity: 0.1;
  pointer-events: none;
}

.category-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}
.cat-bar-row {
  display: flex;
  align-items: center;
  gap: 16px;
}
.cat-bar-label {
  width: 60px;
  font-size: 14px;
  font-weight: 600;
  text-align: right;
  color: var(--text-regular);
}
.cat-bar-track {
  flex: 1;
  height: 12px;
  background: #eee;
  border-radius: 6px;
  overflow: hidden;
}
.cat-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff8c00, var(--primary));
  border-radius: 6px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}
.cat-bar-score {
  width: 40px;
  font-size: 14px;
  font-weight: 800;
  color: var(--primary);
}

.style-tag-area {
  margin-bottom: 24px;
}

.weekly-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 180px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}
.week-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}
.week-bar-wrap {
  width: 24px;
  height: 100px;
  background: #eaeaea;
  border-radius: 4px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}
.week-bar-fill {
  width: 100%;
  background: var(--primary);
  border-radius: 4px;
  transition: height 1s cubic-bezier(0.4, 0, 0.2, 1);
}
.week-label {
  font-size: 12px;
  color: var(--text-muted);
}
.week-count {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-regular);
}
</style>
