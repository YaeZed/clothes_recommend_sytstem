<template>
  <div class="order-list-page container">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/profile' }">个人中心</el-breadcrumb-item>
      <el-breadcrumb-item>我的订单</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="orders-header">
      <h2 class="page-title">我的订单</h2>
      <div class="order-status-tabs">
        <div 
          v-for="tab in statusTabs" 
          :key="tab.value"
          class="status-tab"
          :class="{ active: currentTab === tab.value }"
          @click="currentTab = tab.value"
        >
          {{ tab.label }}
          <span v-if="tab.count" class="count">{{ tab.count }}</span>
        </div>
      </div>
    </div>

    <div v-loading="loading" class="orders-container">
      <div v-if="filteredOrders.length === 0" class="empty-orders">
        <el-empty description="暂时没有相关订单">
          <el-button type="primary" @click="router.push('/products')">去挑选商品</el-button>
        </el-empty>
      </div>

      <div v-else class="order-card-list">
        <div v-for="order in filteredOrders" :key="order.id" class="order-card">
          <div class="order-card-header">
            <div class="header-left">
              <span class="order-date">{{ formatDate(order.createdAt) }}</span>
              <span class="order-no">订单号: {{ order.orderNo }}</span>
              <span class="shop-name"><el-icon><Shop /></el-icon> 衣着搭配官方店</span>
            </div>
            <div class="header-right">
              <span class="order-status" :class="order.status">{{ getStatusLabel(order.status) }}</span>
              <el-button v-if="order.status === 'unpaid'" circle size="small" type="info" plain @click="deleteOrder(order.id)"><el-icon><Delete /></el-icon></el-button>
            </div>
          </div>

          <div class="order-card-content">
            <div class="order-items-column">
              <div v-for="item in order.items" :key="item.id" class="order-item">
                <img :src="item.productImage" class="item-img" />
                <div class="item-info">
                  <div class="item-name">{{ item.productTitle }}</div>
                  <div class="item-attr">
                    <span v-if="item.attributes?.color">颜色:{{ item.attributes.color }}</span>
                    <span v-if="item.attributes?.size">尺码:{{ item.attributes.size }}</span>
                  </div>
                </div>
                <div class="item-price-qty">
                  <div class="p">¥{{ item.price }}</div>
                  <div class="q">x{{ item.quantity }}</div>
                </div>
              </div>
            </div>
            
            <div class="order-user-column">
              <div class="info-label">收货信息</div>
              <div class="info-val">{{ order.receiver.name }} {{ order.receiver.phone }}</div>
              <div class="info-addr">{{ order.receiver.address }}</div>
            </div>

            <div class="order-total-column">
              <div class="total-amount">¥{{ order.totalAmount.toFixed(2) }}</div>
              <div class="shipping-fee">(含运费: ¥0.00)</div>
            </div>

            <div class="order-actions-column">
              <el-button v-if="order.status === 'unpaid'" type="primary" size="small" @click="handlePay(order)">立即付款</el-button>
              <el-button v-if="order.status === 'paid'" type="success" size="small" plain>待发货</el-button>
              <el-button size="small" plain @click="router.push(`/products/${order.items[0]?.productId}`)">查看详情</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrders, payOrder } from '../api/order'
import { ElMessage } from 'element-plus'
import { Shop, Delete } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const currentTab = ref('all')

const statusTabs = [
  { label: '所有订单', value: 'all' },
  { label: '待付款', value: 'unpaid' },
  { label: '待发货', value: 'paid' },
  { label: '待收货', value: 'shipped' },
  { label: '待评价', value: 'completed' }
]

const filteredOrders = computed(() => {
  if (currentTab.value === 'all') return orders.value
  return orders.value.filter(o => o.status === currentTab.value)
})

onMounted(fetchOrders)

async function fetchOrders() {
  loading.value = true
  try {
    const res = await getOrders()
    orders.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()} ${d.getHours()}:${d.getMinutes()}`
}

function getStatusLabel(status) {
  const map = {
    unpaid: '等待买家付款',
    paid: '买家已付款',
    shipped: '卖家已发货',
    completed: '交易成功',
    cancelled: '交易关闭'
  }
  return map[status] || status
}

async function handlePay(order) {
  try {
    await payOrder(order.id)
    ElMessage.success('支付成功')
    fetchOrders()
  } catch (e) {
    console.error(e)
  }
}

async function deleteOrder(id) {
  ElMessage.info('暂不支持删除订单')
}
</script>

<style scoped>
.order-list-page {
  padding: 20px 0 60px;
}
.breadcrumb {
  margin-bottom: 24px;
}

.orders-header {
  background: #fff;
  padding: 24px 24px 0;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  border-bottom: 1px solid #f0f0f0;
}
.page-title {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 24px;
  color: var(--text-primary);
}

.order-status-tabs {
  display: flex;
  gap: 32px;
}
.status-tab {
  padding: 12px 4px;
  font-size: 15px;
  cursor: pointer;
  position: relative;
  color: #666;
  white-space: nowrap;
}
.status-tab.active {
  color: var(--primary);
  font-weight: 700;
}
.status-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary);
  border-radius: 2px;
}
.status-tab .count {
  font-size: 12px;
  color: var(--primary);
  margin-left: 4px;
}

.orders-container {
  min-height: 400px;
}
.empty-orders {
  background: #fff;
  padding: 80px 0;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

.order-card-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.order-card {
  background: #fff;
  border-radius: var(--radius-md);
  border: 1px solid #f0f0f0;
  overflow: hidden;
  transition: all 0.3s;
}
.order-card:hover {
  border-color: #ffaa80;
  box-shadow: 0 4px 12px rgba(255, 80, 0, 0.05);
}

.order-card-header {
  background: #fdfdfd;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  border-bottom: 1px solid #f5f5f5;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}
.order-date {
  font-weight: 700;
  color: #333;
}
.order-no {
  color: #999;
}
.shop-name {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
}

.order-card-content {
  display: flex;
  min-height: 120px;
}

.order-items-column {
  flex: 4;
  padding: 10px 0;
  border-right: 1px solid #f5f5f5;
}
.order-item {
  display: flex;
  padding: 15px 20px;
  gap: 12px;
  align-items: center;
}
.item-img {
  width: 60px;
  height: 72px;
  object-fit: cover;
  border-radius: 4px;
  background: #f5f5f5;
}
.item-info {
  flex: 1;
  min-width: 0;
}
.item-name {
  font-size: 13px;
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.item-attr {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 10px;
}
.item-price-qty {
  text-align: right;
  font-size: 13px;
}
.item-price-qty .p { font-weight: 700; }
.item-price-qty .q { color: #999; margin-top: 4px; }

.order-user-column, .order-total-column, .order-actions-column {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  border-right: 1px solid #f5f5f5;
}

.order-user-column { flex: 2; font-size: 13px; text-align: left; align-items: flex-start; }
.info-label { color: #999; margin-bottom: 8px; }
.info-val { color: #333; font-weight: 600; margin-bottom: 4px; }
.info-addr { color: #888; font-size: 12px; line-height: 1.4; }

.order-total-column { flex: 1.5; }
.total-amount {
  font-size: 16px;
  font-weight: 800;
  color: #333;
  margin-bottom: 4px;
}
.shipping-fee {
  font-size: 12px;
  color: #999;
}

.order-actions-column {
  flex: 1.5;
  border-right: none;
  gap: 10px;
}

.order-status {
  font-weight: 700;
}
.order-status.unpaid { color: var(--primary); }
.order-status.paid { color: #07c160; }
</style>
