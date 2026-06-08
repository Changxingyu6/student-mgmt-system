<template>
  <div class="roles-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新增角色
          </el-button>
        </div>
      </template>

      <!-- 角色列表表格 -->
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="280" />
        <el-table-column prop="name" label="角色名称" width="200" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showEditDialog(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑角色弹窗 -->
    <el-dialog v-model="showRoleDialog" :title="isEdit ? '编辑角色' : '新增角色'" width="500px">
      <el-form :model="roleForm" label-width="100px">
        <el-form-item label="角色名称">
          <el-input v-model="roleForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roleForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRole">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getRoles, createRole, updateRole, deleteRole } from '@/api/role'

const tableData = ref([])
const showRoleDialog = ref(false)
const isEdit = ref(false)
const currentRoleId = ref('')

const roleForm = reactive({
  name: '',
  description: ''
})

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const loadRoles = async () => {
  try {
    const res = await getRoles()
    tableData.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(roleForm, {
    name: '',
    description: ''
  })
  showRoleDialog.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  currentRoleId.value = row.id
  Object.assign(roleForm, {
    name: row.name,
    description: row.description
  })
  showRoleDialog.value = true
}

const handleSaveRole = async () => {
  try {
    if (isEdit.value) {
      await updateRole(currentRoleId.value, roleForm)
      ElMessage.success('更新成功')
    } else {
      await createRole(roleForm)
      ElMessage.success('创建成功')
    }
    showRoleDialog.value = false
    loadRoles()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该角色吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.roles-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>