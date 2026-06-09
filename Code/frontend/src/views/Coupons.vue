<template>
  <div class="coupon-page">
    <h2 class="page-title">营销活动</h2>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="优惠券" name="coupon"></el-tab-pane>
      <el-tab-pane label="我的优惠券" name="userCoupon"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="营销活动" name="activity"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="使用日志" name="useLog"></el-tab-pane>
    </el-tabs>

    <!-- ============ 优惠券 ============ -->
    <div v-show="activeTab === 'coupon'">
      <div class="toolbar">
        <el-button v-if="isAdmin" type="primary" @click="handleAddCoupon">+ 新增优惠券</el-button>
        <el-input v-model="couponSearch.name" placeholder="名称" style="width: 180px; margin-left: 12px" clearable />
        <el-select v-model="couponSearch.type" placeholder="类型" clearable style="width: 120px; margin-left: 8px">
          <el-option label="满减券" :value="1" />
          <el-option label="折扣券" :value="2" />
          <el-option label="无门槛" :value="3" />
        </el-select>
        <el-button @click="loadCoupons" style="margin-left: 8px">搜索</el-button>
      </div>

      <el-table :data="couponList" v-loading="couponLoading" border stripe>
        <el-table-column prop="coupons_no" label="券编号" width="160" />
        <el-table-column prop="coupons_name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ couponTypeMap[row.type] }}</template>
        </el-table-column>
        <el-table-column label="面值" width="100">
          <template #default="{ row }">¥{{ row.face_value }}</template>
        </el-table-column>
        <el-table-column label="使用门槛" width="100">
          <template #default="{ row }">¥{{ row.min_spend }}</template>
        </el-table-column>
        <el-table-column label="总量/已发/已用" width="160">
          <template #default="{ row }">
            {{ row.total_count }} / {{ row.sent_count }} / {{ row.used_count }}
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="220">
          <template #default="{ row }">
            {{ formatDate(row.valid_start_time) }} ~ {{ formatDate(row.valid_end_time) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : (row.status === 0 ? 'info' : 'danger')">
              {{ couponStatusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!isAdmin" size="small" type="primary" @click="handleClaimCoupon(row)">领取</el-button>
            <template v-if="isAdmin">
              <el-button size="small" @click="handleEditCoupon(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDeleteCoupon(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="couponPage.page"
          v-model:page-size="couponPage.page_size"
          :total="couponPage.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadCoupons"
          @size-change="loadCoupons"
        />
      </div>
    </div>

    <!-- ============ 用户优惠券 ============ -->
    <div v-show="activeTab === 'userCoupon'">
      <el-table :data="userCouponList" v-loading="userCouponLoading" border stripe>
        <el-table-column prop="coupon_no" label="券号" width="200" />
        <el-table-column v-if="isAdmin" prop="user_id" label="用户ID" width="160" />
        <el-table-column prop="coupon_id" label="优惠券ID" width="160" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : (row.status === 0 ? 'info' : 'danger')">
              {{ userCouponStatusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="领取时间" width="170">
          <template #default="{ row }">{{ formatDate(row.get_time) }}</template>
        </el-table-column>
        <el-table-column label="使用时间" width="170">
          <template #default="{ row }">{{ formatDate(row.use_time) }}</template>
        </el-table-column>
        <el-table-column label="有效期至" width="170">
          <template #default="{ row }">{{ formatDate(row.valid_end_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="handleDeleteUserCoupon(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="userCouponPage.page"
          v-model:page-size="userCouponPage.page_size"
          :total="userCouponPage.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadUserCoupons"
          @size-change="loadUserCoupons"
        />
      </div>
    </div>

    <!-- ============ 营销活动 ============ -->
    <div v-show="activeTab === 'activity'">
      <div class="toolbar">
        <el-button v-if="isAdmin" type="primary" @click="handleAddActivity">+ 新增活动</el-button>
      </div>

      <el-table :data="activityList" v-loading="activityLoading" border stripe>
        <el-table-column prop="activities_name" label="活动名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="活动类型" width="100">
          <template #default="{ row }">
            {{ row.activities_type === '1' ? '满减' : '折扣' }}
          </template>
        </el-table-column>
        <el-table-column label="面值" width="100">
          <template #default="{ row }">¥{{ row.face_value }}</template>
        </el-table-column>
        <el-table-column label="门槛" width="100">
          <template #default="{ row }">¥{{ row.min_spend }}</template>
        </el-table-column>
        <el-table-column label="活动期" width="220">
          <template #default="{ row }">
            {{ formatDate(row.start_time) }} ~ {{ formatDate(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '生效' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEditActivity(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteActivity(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="activityPage.page"
          v-model:page-size="activityPage.page_size"
          :total="activityPage.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadActivities"
          @size-change="loadActivities"
        />
      </div>
    </div>

    <!-- ============ 使用日志 ============ -->
    <div v-show="activeTab === 'useLog'">
      <el-table :data="useLogList" v-loading="useLogLoading" border stripe>
        <el-table-column prop="user_id" label="用户ID" width="160" />
        <el-table-column prop="user_coupon_id" label="用户券ID" width="160" />
        <el-table-column prop="order_id" label="订单ID" width="160" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '使用成功' : '使用失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="handleDeleteUseLog(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="useLogPage.page"
          v-model:page-size="useLogPage.page_size"
          :total="useLogPage.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadUseLogs"
          @size-change="loadUseLogs"
        />
      </div>
    </div>

    <!-- 优惠券编辑弹窗 -->
    <el-dialog v-model="couponDialogVisible" :title="couponForm.id ? '编辑优惠券' : '新增优惠券'" width="600px">
      <el-form :model="couponForm" label-width="100px">
        <el-form-item label="券编号" v-if="!couponForm.id">
          <el-input v-model="couponForm.coupons_no" />
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="couponForm.coupons_name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="couponForm.type" style="width: 100%">
            <el-option label="满减券" :value="1" />
            <el-option label="折扣券" :value="2" />
            <el-option label="无门槛" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="面值">
          <el-input-number v-model="couponForm.face_value" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="使用门槛">
          <el-input-number v-model="couponForm.min_spend" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="总量">
          <el-input-number v-model="couponForm.total_count" :min="0" />
        </el-form-item>
        <el-form-item label="生效时间">
          <el-date-picker v-model="couponForm.valid_start_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="失效时间">
          <el-date-picker v-model="couponForm.valid_end_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" v-if="couponForm.id">
          <el-select v-model="couponForm.status" style="width: 100%">
            <el-option label="下架" :value="0" />
            <el-option label="生效" :value="1" />
            <el-option label="过期" :value="2" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="couponDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCoupon">保存</el-button>
      </template>
    </el-dialog>

    <!-- 营销活动编辑弹窗 -->
    <el-dialog v-model="activityDialogVisible" :title="activityForm.id ? '编辑活动' : '新增活动'" width="600px">
      <el-form :model="activityForm" label-width="100px">
        <el-form-item label="活动名称">
          <el-input v-model="activityForm.activities_name" />
        </el-form-item>
        <el-form-item label="活动类型">
          <el-radio-group v-model="activityForm.activities_type">
            <el-radio label="1">满减</el-radio>
            <el-radio label="2">折扣</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="面值">
          <el-input-number v-model="activityForm.face_value" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="门槛">
          <el-input-number v-model="activityForm.min_spend" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker v-model="activityForm.start_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker v-model="activityForm.end_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" v-if="activityForm.id">
          <el-radio-group v-model="activityForm.status">
            <el-radio :value="1">生效</el-radio>
            <el-radio :value="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="activityDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveActivity">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listCoupons, createCoupon, updateCoupon, deleteCoupon,
  listUserCoupons, createUserCoupon, deleteUserCoupon, receiveCoupon,
  listActivities, createActivity, updateActivity, deleteActivity,
  listUseLogs, deleteUseLog
} from '@/api/coupon'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const activeTab = ref('coupon')
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'

const couponTypeMap = { 1: '满减券', 2: '折扣券', 3: '无门槛' }
const couponStatusMap = { 0: '下架', 1: '生效', 2: '过期' }
const userCouponStatusMap = { 0: '未领取', 1: '已领取', 2: '已过期' }

// ============ 优惠券 ============
const couponLoading = ref(false)
const couponList = ref([])
const couponPage = reactive({ page: 1, page_size: 10, total: 0 })
const couponSearch = reactive({ name: '', type: '' })
const couponDialogVisible = ref(false)
const couponForm = reactive({
  id: '', coupons_no: '', coupons_name: '', type: 1,
  face_value: 0, min_spend: 0, total_count: 0,
  valid_start_time: '', valid_end_time: '', status: 1
})

const loadCoupons = async () => {
  couponLoading.value = true
  try {
    const res = await listCoupons({
      page: couponPage.page, page_size: couponPage.page_size,
      coupons_name: couponSearch.name || undefined,
      type: couponSearch.type || undefined
    })
    couponList.value = res.data?.items || res.data || []
    couponPage.total = res.data?.total || 0
  } catch (e) {
    console.error(e)
    ElMessage.error('加载优惠券失败')
  } finally {
    couponLoading.value = false
  }
}

const handleAddCoupon = () => {
  Object.assign(couponForm, {
    id: '', coupons_no: '', coupons_name: '', type: 1,
    face_value: 0, min_spend: 0, total_count: 0,
    valid_start_time: '', valid_end_time: '', status: 1
  })
  couponDialogVisible.value = true
}

const handleEditCoupon = async (row) => {
  try {
    const res = await listCoupons({ coupons_no: row.coupons_no, page: 1, page_size: 1 })
    const data = (res.data && res.data[0]) || row
    Object.assign(couponForm, data)
    couponDialogVisible.value = true
  } catch (e) {
    Object.assign(couponForm, row)
    couponDialogVisible.value = true
  }
}

const handleSaveCoupon = async () => {
  if (!couponForm.coupons_name || !couponForm.valid_start_time || !couponForm.valid_end_time) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    if (couponForm.id) {
      await updateCoupon(couponForm.id, couponForm)
    } else {
      await createCoupon(couponForm)
    }
    ElMessage.success('保存成功')
    couponDialogVisible.value = false
    loadCoupons()
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '保存失败')
  }
}

const handleDeleteCoupon = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除优惠券"${row.coupons_name}"？`, '提示', { type: 'warning' })
    await deleteCoupon(row.id)
    ElMessage.success('删除成功')
    loadCoupons()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// 领取优惠券
const handleClaimCoupon = async (row) => {
  const userId = userStore.userInfo?.id
  if (!userId) { 
    ElMessage.warning('请先登录')
    return 
  }
  
  try {
    const res = await receiveCoupon(row.id, userId)
    if (res.code === 200) {
      ElMessage.success('领取成功')
      loadCoupons() // 刷新列表更新库存
    } else {
      ElMessage.error(res.message || '领取失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || e.response?.data?.detail || '领取失败')
  }
}

// ============ 用户优惠券 ============
const userCouponLoading = ref(false)
const userCouponList = ref([])
const userCouponPage = reactive({ page: 1, page_size: 10, total: 0 })

const loadUserCoupons = async () => {
  userCouponLoading.value = true
  try {
    const params = { page: userCouponPage.page, page_size: userCouponPage.page_size }
    if (!isAdmin.value) {
      params.user_id = userStore.userInfo?.id
    }
    const res = await listUserCoupons(params)
    let list = res.data?.items || res.data || []
    if (!isAdmin.value && userStore.userInfo?.id) {
      list = list.filter(c => c.user_id === userStore.userInfo.id)
    }
    userCouponList.value = list
    userCouponPage.total = res.data?.total || list.length || 0
  } catch (e) {
    console.error(e)
  } finally {
    userCouponLoading.value = false
  }
}

const handleDeleteUserCoupon = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该用户优惠券？', '提示', { type: 'warning' })
    await deleteUserCoupon(row.id)
    ElMessage.success('删除成功')
    loadUserCoupons()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ============ 营销活动 ============
const activityLoading = ref(false)
const activityList = ref([])
const activityPage = reactive({ page: 1, page_size: 10, total: 0 })
const activityDialogVisible = ref(false)
const activityForm = reactive({
  id: '', activities_name: '', activities_type: '1',
  face_value: 0, min_spend: 0,
  start_time: '', end_time: '', status: 1
})

const loadActivities = async () => {
  activityLoading.value = true
  try {
    const res = await listActivities({ page: activityPage.page, page_size: activityPage.page_size })
    activityList.value = res.data?.items || res.data || []
    activityPage.total = res.data?.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    activityLoading.value = false
  }
}

const handleAddActivity = () => {
  Object.assign(activityForm, {
    id: '', activities_name: '', activities_type: '1',
    face_value: 0, min_spend: 0,
    start_time: '', end_time: '', status: 1
  })
  activityDialogVisible.value = true
}

const handleEditActivity = (row) => {
  Object.assign(activityForm, row)
  activityDialogVisible.value = true
}

const handleSaveActivity = async () => {
  if (!activityForm.activities_name || !activityForm.start_time || !activityForm.end_time) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    if (activityForm.id) {
      await updateActivity(activityForm.id, activityForm)
    } else {
      await createActivity(activityForm)
    }
    ElMessage.success('保存成功')
    activityDialogVisible.value = false
    loadActivities()
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '保存失败')
  }
}

const handleDeleteActivity = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除活动"${row.activities_name}"？`, '提示', { type: 'warning' })
    await deleteActivity(row.id)
    ElMessage.success('删除成功')
    loadActivities()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ============ 使用日志 ============
const useLogLoading = ref(false)
const useLogList = ref([])
const useLogPage = reactive({ page: 1, page_size: 10, total: 0 })

const loadUseLogs = async () => {
  useLogLoading.value = true
  try {
    const res = await listUseLogs({ page: useLogPage.page, page_size: useLogPage.page_size })
    useLogList.value = res.data?.items || res.data || []
    useLogPage.total = res.data?.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    useLogLoading.value = false
  }
}

const handleDeleteUseLog = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该日志？', '提示', { type: 'warning' })
    await deleteUseLog(row.id)
    ElMessage.success('删除成功')
    loadUseLogs()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleTabChange = (tab) => {
  if (tab === 'coupon') loadCoupons()
  else if (tab === 'userCoupon') loadUserCoupons()
  else if (tab === 'activity') loadActivities()
  else if (tab === 'useLog') loadUseLogs()
}

onMounted(() => {
  loadCoupons()
})
</script>

<style scoped>
.coupon-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
.toolbar { margin-bottom: 16px; display: flex; align-items: center; }
.pagination { margin-top: 20px; text-align: right; }
</style>
