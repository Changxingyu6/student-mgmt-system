<template>
  <div class="addresses-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>地址管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新增地址
          </el-button>
        </div>
      </template>

      <!-- 地址列表 -->
      <div class="address-list">
        <el-card v-for="address in tableData" :key="address.id" class="address-card">
          <div class="address-info">
            <div class="address-header">
              <span class="receiver">{{ address.receiver_name }}</span>
              <span class="phone">{{ address.receiver_phone }}</span>
              <el-tag v-if="address.is_default" type="success" size="small">默认</el-tag>
            </div>
            <div class="address-detail">
              {{ address.province }} {{ address.city }} {{ address.district }} {{ address.detail_address }}
            </div>
          </div>
          <div class="address-actions">
            <el-button type="primary" size="small" @click="showEditDialog(address)">
              编辑
            </el-button>
            <el-button v-if="!address.is_default" type="success" size="small" @click="handleSetDefault(address)">
              设为默认
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(address)">
              删除
            </el-button>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 创建/编辑地址弹窗 -->
    <el-dialog v-model="showAddressDialog" :title="isEdit ? '编辑地址' : '新增地址'" width="500px">
      <el-form :model="addressForm" label-width="100px">
        <el-form-item label="收货人">
          <el-input v-model="addressForm.receiver_name" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="addressForm.receiver_phone" />
        </el-form-item>
        <el-form-item label="省份">
          <el-input v-model="addressForm.province" />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="addressForm.city" />
        </el-form-item>
        <el-form-item label="区县">
          <el-input v-model="addressForm.district" />
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input v-model="addressForm.detail_address" type="textarea" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="addressForm.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddressDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAddress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getAddresses, createAddress, updateAddress, deleteAddress, setDefaultAddress } from '@/api/address'

const tableData = ref([])
const showAddressDialog = ref(false)
const isEdit = ref(false)
const currentAddressId = ref('')

const addressForm = reactive({
  receiver_name: '',
  receiver_phone: '',
  province: '',
  city: '',
  district: '',
  detail_address: '',
  is_default: false
})

const loadAddresses = async () => {
  try {
    const res = await getAddresses()
    tableData.value = res.data.data || []
  } catch (error) {
    console.error(error)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(addressForm, {
    receiver_name: '',
    receiver_phone: '',
    province: '',
    city: '',
    district: '',
    detail_address: '',
    is_default: false
  })
  showAddressDialog.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  currentAddressId.value = row.id
  Object.assign(addressForm, {
    receiver_name: row.receiver_name,
    receiver_phone: row.receiver_phone,
    province: row.province,
    city: row.city,
    district: row.district,
    detail_address: row.detail_address,
    is_default: row.is_default
  })
  showAddressDialog.value = true
}

const handleSaveAddress = async () => {
  try {
    if (isEdit.value) {
      await updateAddress(currentAddressId.value, addressForm)
      ElMessage.success('更新成功')
    } else {
      await createAddress(addressForm)
      ElMessage.success('创建成功')
    }
    showAddressDialog.value = false
    loadAddresses()
  } catch (error) {
    console.error(error)
  }
}

const handleSetDefault = async (row) => {
  try {
    await setDefaultAddress(row.id)
    ElMessage.success('设置成功')
    loadAddresses()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该地址吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteAddress(row.id)
    ElMessage.success('删除成功')
    loadAddresses()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

onMounted(() => {
  loadAddresses()
})
</script>

<style scoped>
.addresses-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.address-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.address-card {
  width: 400px;
}

.address-info {
  margin-bottom: 10px;
}

.address-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.receiver {
  font-weight: bold;
  font-size: 16px;
}

.phone {
  color: #666;
}

.address-detail {
  color: #333;
  font-size: 14px;
}

.address-actions {
  display: flex;
  gap: 10px;
}
</style>