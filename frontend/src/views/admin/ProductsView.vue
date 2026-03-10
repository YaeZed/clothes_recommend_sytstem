<template>
  <div>
    <!-- 搜索栏 -->
    <div class="admin-toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索商品名称..."
        clearable
        style="width: 260px"
        @keyup.enter="load"
        @clear="load"
      >
        <template #prefix
          ><el-icon><Search /></el-icon
        ></template>
      </el-input>
      <el-select
        v-model="filterCat"
        placeholder="全部类目"
        clearable
        style="width: 140px"
        @change="load"
      >
        <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <el-button type="success" @click="openDialog(null)">+ 新增商品</el-button>
    </div>

    <el-table
      :data="products"
      v-loading="loading"
      stripe
      border
      style="margin-top: 0"
    >
      <el-table-column label="图片" width="80">
        <template #default="{ row }">
          <img
            v-if="row.images?.[0]"
            :src="row.images[0]"
            style="
              width: 52px;
              height: 64px;
              object-fit: cover;
              border-radius: 4px;
            "
          />
          <span v-else style="color: #bbb; font-size: 12px">无图</span>
        </template>
      </el-table-column>
      <el-table-column label="ID" prop="id" width="70" />
      <el-table-column
        label="商品名"
        prop="title"
        min-width="200"
        show-overflow-tooltip
      />
      <el-table-column label="类目" prop="category" width="100" />
      <el-table-column label="风格" prop="style" width="100" />
      <el-table-column label="价格" width="100">
        <template #default="{ row }">¥{{ row.price }}</template>
      </el-table-column>
      <el-table-column label="销量" prop="salesCount" width="90" />
      <el-table-column label="上架" width="90">
        <template #default="{ row }"
          ><el-tag :type="row.isOnSale ? 'success' : 'danger'">{{
            row.isOnSale ? "上架" : "下架"
          }}</el-tag></template
        >
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteProduct(row.id)"
            >删除</el-button
          >
        </template>
      </el-table-column>
    </el-table>

    <div style="display: flex; justify-content: center; margin-top: 20px">
      <el-pagination
        v-model:current-page="page"
        :page-size="20"
        :total="total"
        layout="prev,pager,next,total"
        @current-change="load"
      />
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editForm.id ? '编辑商品' : '新增商品'"
      width="600px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="商品名"
          ><el-input v-model="editForm.title"
        /></el-form-item>
        <el-form-item label="类目">
          <el-select v-model="editForm.category"
            ><el-option v-for="c in categories" :key="c" :label="c" :value="c"
          /></el-select>
        </el-form-item>
        <el-form-item label="风格">
          <el-select v-model="editForm.style"
            ><el-option v-for="s in styles" :key="s" :label="s" :value="s"
          /></el-select>
        </el-form-item>
        <el-form-item label="价格"
          ><el-input-number v-model="editForm.price" :precision="2"
        /></el-form-item>
        <el-form-item label="库存"
          ><el-input-number v-model="editForm.stock" :min="0"
        /></el-form-item>
        <el-form-item label="状态"
          ><el-switch
            v-model="editForm.is_on_sale"
            active-text="上架"
            inactive-text="下架"
        /></el-form-item>
        <el-form-item label="描述"
          ><el-input v-model="editForm.description" type="textarea" :rows="3"
        /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct" :loading="saving"
          >保存</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import request from "../../api/request";

const products = ref([]);
const total = ref(0);
const page = ref(1);
const loading = ref(false);
const saving = ref(false);
const keyword = ref("");
const filterCat = ref("");
const dialogVisible = ref(false);
const categories = [
  "上衣",
  "裤子",
  "裙子",
  "外套",
  "卫衣",
  "鞋子",
  "配饰",
  "其他",
];
const styles = ["休闲", "正式", "运动", "街头", "复古", "简约", "时尚"];

const editForm = reactive({
  id: null,
  title: "",
  category: "",
  style: "",
  price: 0,
  stock: 0,
  is_on_sale: true,
  description: "",
});

async function load() {
  loading.value = true;
  const res = await request.get("/admin/products", {
    params: {
      page: page.value,
      perPage: 20,
      keyword: keyword.value,
      category: filterCat.value,
    },
  });
  products.value = res.data.items;
  total.value = res.data.total;
  loading.value = false;
}

function openDialog(row) {
  if (row) Object.assign(editForm, row, { is_on_sale: row.isOnSale });
  else
    Object.assign(editForm, {
      id: null,
      title: "",
      category: "",
      style: "",
      price: 0,
      stock: 0,
      is_on_sale: true,
      description: "",
    });
  dialogVisible.value = true;
}

async function saveProduct() {
  saving.value = true;
  if (editForm.id)
    await request.put(`/admin/products/${editForm.id}`, editForm);
  else await request.post("/admin/products", editForm);
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  saving.value = false;
  load();
}

async function deleteProduct(id) {
  await ElMessageBox.confirm("确认删除？", "提示", { type: "warning" });
  await request.delete(`/admin/products/${id}`);
  ElMessage.success("删除成功");
  load();
}

onMounted(load);
</script>

<style scoped>
.admin-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
</style>
