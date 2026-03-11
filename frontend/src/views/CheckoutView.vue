<template>
  <div class="checkout-page container">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>确认订单</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="checkout-container">
      <!-- 左侧：主要流程 -->
      <div class="checkout-main">
        <!-- 1. 收货地址选择 -->
        <div class="checkout-section">
          <h3 class="section-title"><el-icon><Location /></el-icon> 确认收货地址</h3>
          <div class="address-list">
            <div 
              v-for="(addr, idx) in addressList" 
              :key="idx"
              class="address-card"
              :class="{ active: selectedAddress === idx }"
              @click="selectedAddress = idx"
            >
              <div class="addr-header">
                <span class="addr-name">{{ addr.receiver }}</span>
                <span class="addr-phone">{{ addr.phone }}</span>
                <el-tag v-if="addr.isDefault" size="small" type="danger" effect="plain">默认</el-tag>
              </div>
              <div class="addr-detail">
                {{ addr.province }} {{ addr.city }} {{ addr.district }} {{ addr.detail }}
              </div>
              <div class="addr-actions">
                <el-button link type="primary">修改</el-button>
              </div>
              <div class="active-badge"><el-icon><Check /></el-icon></div>
            </div>
            
            <div class="add-address-card" @click="ElMessage.info('功能开发中...')">
              <el-icon><Plus /></el-icon>
              <span>使用新地址</span>
            </div>
          </div>
        </div>

        <!-- 2. 商品确认 -->
        <div class="checkout-section">
          <h3 class="section-title"><el-icon><ShoppingBag /></el-icon> 确认订单信息</h3>
          <div class="order-table-header">
            <div class="col-info">店铺宝贝</div>
            <div class="col-attr">商品属性</div>
            <div class="col-price">单价</div>
            <div class="col-qty">数量</div>
            <div class="col-subtotal">小计</div>
          </div>
          
          <div class="shop-group">
            <div class="shop-header">
              <el-icon><Shop /></el-icon>
              <span class="shop-name">衣着搭配官方店</span>
            </div>
            
            <div v-for="item in cartStore.items" :key="item.id" class="order-product-row">
              <div class="col-info">
                <img :src="item.product?.images?.[0]" class="p-img" />
                <div class="p-details">
                  <div class="p-name">{{ item.product?.title }}</div>
                  <div class="p-tags">
                    <el-tag size="small" effect="plain" type="info">七天无理由退换</el-tag>
                  </div>
                </div>
              </div>
              <div class="col-attr">
                <div v-if="item.attributes?.color" class="attr-item">颜色：{{ item.attributes.color }}</div>
                <div v-if="item.attributes?.size" class="attr-item">尺码：{{ item.attributes.size }}</div>
              </div>
              <div class="col-price">¥{{ item.product?.price }}</div>
              <div class="col-qty">{{ item.quantity }}</div>
              <div class="col-subtotal">¥{{ (item.product?.price * item.quantity).toFixed(2) }}</div>
            </div>
          </div>
          
          <div class="order-remark">
            <span>给卖家留言：</span>
            <el-input 
              v-model="remark" 
              placeholder="选填：填写内容已和卖家协商确认" 
              type="textarea" 
              :rows="1"
              resize="none"
              class="remark-input"
            />
          </div>
        </div>
      </div>

      <!-- 右侧：固定结算栏/悬浮栏 -->
      <div class="checkout-footer">
        <div class="footer-inner">
          <div class="final-info">
            <div class="info-row">
              <span class="label">实付款：</span>
              <span class="final-price">¥{{ cartStore.totalPrice.toFixed(2) }}</span>
            </div>
            <div class="info-row addr-preview" v-if="addressList[selectedAddress]">
              <span class="label">寄送至：</span>
              <span>{{ addressList[selectedAddress].province }} {{ addressList[selectedAddress].city }} {{ addressList[selectedAddress].detail }}</span>
            </div>
            <div class="info-row user-preview" v-if="addressList[selectedAddress]">
              <span class="label">收货人：</span>
              <span>{{ addressList[selectedAddress].receiver }} {{ addressList[selectedAddress].phone }}</span>
            </div>
          </div>
          <div class="submit-bar">
            <el-button 
              type="primary" 
              class="submit-btn" 
              size="large" 
              :loading="submitting"
              @click="submitOrder"
            >
              提交订单
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 支付弹窗 -->
    <el-dialog
      v-model="payDialog.visible"
      title="模拟支付"
      width="400px"
      align-center
      :close-on-click-modal="false"
    >
      <div class="pay-container">
        <div class="pay-amount">
          <span class="label">待支付金额</span>
          <span class="price">¥{{ cartStore.totalPrice.toFixed(2) }}</span>
        </div>
        <div class="pay-methods">
          <div 
            v-for="m in payMethods" 
            :key="m.id" 
            class="pay-method-item"
            :class="{ active: payDialog.method === m.id }"
            @click="payDialog.method = m.id"
          >
            <el-icon v-if="m.id === 'alipay'" color="#1677ff"><WalletFilled /></el-icon>
            <el-icon v-else color="#07c160"><CircleCheckFilled /></el-icon>
            <span>{{ m.name }}</span>
            <div class="check-mark" v-if="payDialog.method === m.id"><el-icon><Check /></el-icon></div>
          </div>
        </div>
        <div class="pay-tips">提示：点击确认将模拟支付成功并跳转至订单页</div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="payDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="confirmPayment" :loading="paying">
            确认支付
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../store/cart'
import { createOrder, payOrder } from '../api/order'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Location, Check, Plus, ShoppingBag, Shop, 
  WalletFilled, CircleCheckFilled 
} from '@element-plus/icons-vue'

const router = useRouter()
const cartStore = useCartStore()

const submitting = ref(false)
const paying = ref(false)
const remark = ref('')
const selectedAddress = ref(0)

const addressList = ref([
  {
    receiver: '张小强',
    phone: '138****8888',
    province: '广东省',
    city: '深圳市',
    district: '南山区',
    detail: '科苑路科兴科学园 B1 栋 20层',
    isDefault: true
  },
  {
    receiver: '张三',
    phone: '135****1234',
    province: '北京市',
    city: '北京市',
    district: '朝阳区',
    detail: '三里屯 SOHO 5号商场 202',
    isDefault: false
  }
])

const payDialog = ref({
  visible: false,
  orderId: null,
  method: 'alipay'
})

const payMethods = [
  { id: 'alipay', name: '支付宝' },
  { id: 'wechat', name: '微信支付' }
]

onMounted(async () => {
  if (cartStore.items.length === 0) {
    await cartStore.load()
    if (cartStore.items.length === 0) {
      ElMessage.warning('购物车是空的，返回浏览商品吧')
      router.push('/products')
    }
  }
})

async function submitOrder() {
  submitting.value = true
  try {
    const res = await createOrder({
      receiver: {
        name: addressList.value[selectedAddress.value].receiver,
        phone: addressList.value[selectedAddress.value].phone,
        address: `${addressList.value[selectedAddress.value].province}${addressList.value[selectedAddress.value].city}${addressList.value[selectedAddress.value].detail}`
      },
      remark: remark.value
    })
    
    payDialog.value.orderId = res.data.id
    payDialog.value.visible = true
    
    // 成功下单后清空本地购物车（后端 API 已经清空了数据库中的购物车）
    cartStore.items = []
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

async function confirmPayment() {
  paying.value = true
  try {
    await payOrder(payDialog.value.orderId)
    ElMessage.success('支付成功！')
    router.push('/profile?tab=orders') // 或者跳转到专门的订单页
  } catch (e) {
    console.error(e)
  } finally {
    paying.value = false
    payDialog.value.visible = false
  }
}
</script>

<style scoped>
.checkout-page {
  padding: 20px 0 100px;
}
.breadcrumb {
  margin-bottom: 24px;
}

.checkout-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.checkout-section {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-primary);
}

/* 地址列表 */
.address-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.address-card, .add-address-card {
  width: 270px;
  height: 140px;
  border: 2px solid #eee;
  border-radius: var(--radius-md);
  padding: 16px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s;
}
.address-card:hover {
  border-color: #ffaa80;
}
.address-card.active {
  border-color: var(--primary);
  background: #fffcfb;
}

.addr-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.addr-name {
  font-weight: 700;
  font-size: 15px;
}
.addr-phone {
  color: #666;
}
.addr-detail {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.addr-actions {
  position: absolute;
  right: 12px;
  bottom: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}
.address-card:hover .addr-actions {
  opacity: 1;
}

.active-badge {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 24px;
  height: 24px;
  background: var(--primary);
  color: #fff;
  display: none;
  align-items: center;
  justify-content: center;
  clip-path: polygon(100% 0, 100% 100%, 0 100%);
}
.address-card.active .active-badge {
  display: flex;
}
.active-badge .el-icon {
  transform: translate(3px, 3px);
  font-size: 12px;
}

.add-address-card {
  border: 2px dashed #eee;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  gap: 8px;
}
.add-address-card:hover {
  border-color: var(--primary);
  color: var(--primary);
}

/* 订单表格 */
.order-table-header {
  display: flex;
  padding: 12px 0;
  border-bottom: 2px solid #f1f1f1;
  font-size: 13px;
  color: #999;
}
.shop-group {
  margin-top: 10px;
}
.shop-header {
  padding: 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
}
.shop-name {
  color: #333;
}

.order-product-row {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f9f9f9;
}

.col-info { flex: 4; display: flex; gap: 12px; align-items: center; }
.col-attr { flex: 2; font-size: 12px; color: #999; }
.col-price { flex: 1.5; text-align: center; font-weight: 600; }
.col-qty { flex: 1; text-align: center; }
.col-subtotal { flex: 1.5; text-align: right; font-weight: 700; color: #333; }

.p-img {
  width: 60px;
  height: 72px;
  object-fit: cover;
  border-radius: 4px;
  background: #f5f5f5;
}
.p-name {
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.order-remark {
  margin-top: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fdfdfd;
  border-radius: var(--radius-md);
}
.remark-input {
  flex: 1;
}

/* 底部结算栏 */
.checkout-footer {
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #eee;
  box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
  margin-top: 20px;
  z-index: 100;
}
.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: flex-end;
  padding: 15px 24px;
}

.final-info {
  text-align: right;
  margin-right: 30px;
}
.info-row {
  margin-bottom: 6px;
  font-size: 13px;
  color: #666;
}
.final-price {
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
  vertical-align: middle;
}
.addr-preview, .user-preview {
  font-size: 12px;
  color: #999;
}

.submit-btn {
  width: 180px;
  height: 50px;
  font-size: 18px;
  font-weight: 700;
  border-radius: 25px;
}

/* 支付弹窗 */
.pay-container {
  padding: 10px 0;
}
.pay-amount {
  text-align: center;
  margin-bottom: 24px;
}
.pay-amount .label {
  display: block;
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}
.pay-amount .price {
  font-size: 32px;
  font-weight: 800;
  color: #333;
}
.pay-methods {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.pay-method-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: var(--radius-md);
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}
.pay-method-item:hover {
  background: #f9f9f9;
}
.pay-method-item.active {
  border-color: var(--primary);
  background: #fffafa;
}
.pay-method-item .el-icon {
  font-size: 24px;
}
.pay-method-item span {
  font-weight: 600;
}
.check-mark {
  position: absolute;
  right: 16px;
  color: var(--primary);
}
.pay-tips {
  margin-top: 20px;
  font-size: 12px;
  color: #999;
  text-align: center;
}
</style>
