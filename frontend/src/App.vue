<script setup>
import { ref, onMounted } from 'vue'
import CharacterFilter from './components/CharacterFilter.vue'
import AddTeamModal from './components/AddTeamModal.vue'
import EditTeamModal from './components/EditTeamModal.vue'
import TeamCard from './components/TeamCard.vue'
import TeamDetailModal from './components/TeamDetailModal.vue'
import AuthModal from './components/AuthModal.vue'
import UserMenu from './components/UserMenu.vue'
import { teamAPI } from './services/api'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

const team = ref([])
const filterRef = ref(null)
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDetailModal = ref(false)
const showAuthModal = ref(false)
const currentTeam = ref(null)
const teams = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCharacterIds = ref([])
const pagination = ref({
  page: 1,
  page_size: 10,
  count: 0
})

const isGridView = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')
const showConfirmDialog = ref(false)
const confirmCallback = ref(null)
const confirmMessage = ref('')

// 加载配队列表
const loadTeams = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.page_size
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (selectedCharacterIds.value.length > 0) {
      params.character_ids = selectedCharacterIds.value.join(',')
    }
    const data = await teamAPI.getTeams(params)
    teams.value = data.results || data
    pagination.value.count = data.count || data.length
  } catch (error) {
    console.error('Failed to load teams:', error)
  } finally {
    loading.value = false
  }
}

// 搜索防抖
let searchTimer = null
const handleSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.value.page = 1
    loadTeams()
  }, 300)
}

const handleTeamChange = (newTeam) => {
  team.value = newTeam
  selectedCharacterIds.value = newTeam.map(c => c.id)
  pagination.value.page = 1
  loadTeams()
}

const openAddModal = () => {
  if (!authStore.isAuthenticated) {
    showAuthModal.value = true
    return
  }
  if (filterRef.value) filterRef.value.clearTeamSelection()
  team.value = []
  showAddModal.value = true
}

const saveNewTeam = async (teamData) => {
  try {
    const apiData = {
      name: teamData.name,
      remark: teamData.remark || '',
      axis_length: teamData.axisLength ? parseInt(teamData.axisLength) : null,
      dps: teamData.dps ? parseInt(teamData.dps) : null,
      difficulty: teamData.difficulty,
      environment: teamData.environment,
      contributors: authStore.user?.username || '',
      created_by_id: authStore.user?.id,
      team_characters: teamData.characters.map((char, index) => ({
        character_id: char.id,
        character_name: char.name,
        energy: char.energy || '',
        order: index
      })),
      axes: teamData.axes.map((axis, index) => {
        const charObjects = axis.rotationData.characters || []
        const segmentsData = axis.rotationData.segments || {}
        
        const result = {
          name: axis.name,
          video_url: axis.videoUrl ? axis.videoUrl.replace('/media/videos/', '') : null,
          total_duration: axis.rotationData.totalDuration,
          segments_data: segmentsData,
          characters: charObjects.map(c => ({
            name: c.name,
            segments: c.segments || []
          })),
          order: index
        }
        
        charObjects.forEach(c => {
          result.segments_data[c.name] = c.segments || []
        })
        
        return result
      })
    }
    
    await teamAPI.createTeam(apiData)
    showAddModal.value = false
    await loadTeams()
  } catch (error) {
    console.error('Failed to save team:', error)
    alert('保存失败：' + error.message)
  }
}

const saveEditedTeam = async (teamData) => {
  try {
    const apiData = {
      name: teamData.name,
      remark: teamData.remark || '',
      axis_length: teamData.axisLength ? parseInt(teamData.axisLength) : null,
      dps: teamData.dps ? parseInt(teamData.dps) : null,
      difficulty: teamData.difficulty,
      environment: teamData.environment,
      contributors: authStore.user?.username || '',
      team_characters: teamData.characters.map((char, index) => ({
        character_id: char.id,
        character_name: char.name,
        energy: char.energy || '',
        order: index
      })),
      axes: teamData.axes.map((axis, index) => {
        const charObjects = axis.rotationData.characters || []
        const segmentsData = axis.rotationData.segments || {}
        
        const result = {
          name: axis.name,
          video_url: axis.videoUrl ? axis.videoUrl.replace('/media/videos/', '') : null,
          total_duration: axis.rotationData.totalDuration,
          segments_data: segmentsData,
          characters: charObjects.map(c => ({
            name: c.name,
            segments: c.segments || []
          })),
          order: index
        }
        
        charObjects.forEach(c => {
          result.segments_data[c.name] = c.segments || []
        })
        
        return result
      })
    }
    
    await teamAPI.updateTeam(teamData.id, apiData)
    showEditModal.value = false
    currentTeam.value = null
    await loadTeams()
  } catch (error) {
    console.error('Failed to update team:', error)
    alert('更新失败：' + error.message)
  }
}

const confirmDialog = (message) => {
  return new Promise((resolve) => {
    confirmMessage.value = message
    showConfirmDialog.value = true
    confirmCallback.value = () => {
      showConfirmDialog.value = false
      resolve(true)
    }
    // 用户取消时
    setTimeout(() => {
      if (showConfirmDialog.value && !confirmCallback.value) {
        showConfirmDialog.value = false
        resolve(false)
      }
    }, 0)
  })
}

const deleteTeam = async (id, createdBy) => {
  if (!authStore.isAuthenticated) {
    showAuthModal.value = true
    return
  }
  
  if (authStore.user && authStore.user.id !== createdBy) {
    toastMessage.value = '只能删除自己的配队'
    toastType.value = 'error'
    showToast.value = true
    setTimeout(() => showToast.value = false, 3000)
    return
  }
  
  const confirmed = await confirmDialog('确定要删除这个配队吗？')
  if (!confirmed) return
  
  try {
    await teamAPI.deleteTeam(id)
    toastMessage.value = '删除成功'
    toastType.value = 'success'
    showToast.value = true
    setTimeout(() => showToast.value = false, 3000)
    await loadTeams()
  } catch (error) {
    console.error('Failed to delete team:', error)
    toastMessage.value = '删除失败：' + error.message
    toastType.value = 'error'
    showToast.value = true
    setTimeout(() => showToast.value = false, 3000)
  }
}

const handleViewDetail = (t) => {
  currentTeam.value = t
  showDetailModal.value = true
}

const handleViewTeam = (t) => {
  currentTeam.value = t
  showDetailModal.value = true
}

const handleEditTeam = (t) => {
  if (!authStore.isAuthenticated) {
    showAuthModal.value = true
    return
  }
  if (authStore.user?.id !== t.created_by?.id) {
    toastMessage.value = '只能编辑自己的配队'
    toastType.value = 'error'
    showToast.value = true
    setTimeout(() => showToast.value = false, 3000)
    return
  }
  currentTeam.value = t
  showEditModal.value = true
}

const onLoginSuccess = async () => {
  await loadTeams()
}

const handleDeleteTeam = async (id, createdBy) => {
  await deleteTeam(id, createdBy)
}

const handleDeleteTeamFromMyTeams = async (team) => {
  const confirmed = await confirmDialog('确定要删除这个配队吗？')
  if (!confirmed) return
  
  try {
    await teamAPI.deleteTeam(team.id)
    toastMessage.value = '删除成功'
    toastType.value = 'success'
    showToast.value = true
    setTimeout(() => showToast.value = false, 3000)
  } catch (error) {
    console.error('Failed to delete team:', error)
    toastMessage.value = '删除失败：' + error.message
    toastType.value = 'error'
    showToast.value = true
    setTimeout(() => showToast.value = false, 3000)
  }
}

onMounted(async () => {
  document.documentElement.classList.add('dark')
  await authStore.checkAuth()
  await loadTeams()
})
</script>

<template>
  <div class="h-screen flex flex-col bg-[var(--bg-primary)] overflow-hidden">
    <header class="flex-shrink-0 bg-[var(--bg-secondary)] shadow-sm border-b border-[var(--border-color)]">
      <div class="container mx-auto px-5 py-2.5 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <img src="/assets/logo.png" alt="logo" class="w-10 h-10 rounded-lg object-contain" />
          <div>
            <h1 class="text-lg font-semibold text-[var(--text-primary)]">
              鸣潮排轴工具
            </h1>
            <p class="text-[10px] text-[var(--text-tertiary)]">配队管理 · 输出轴记录</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <template v-if="authStore.isAuthenticated">
            <UserMenu @view-team="handleViewTeam" @edit-team="handleEditTeam" @delete-team="handleDeleteTeamFromMyTeams" />
          </template>
          <template v-else>
            <button
              @click="showAuthModal = true"
              class="px-4 py-2 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-sm text-[var(--text-secondary)] hover:text-[var(--accent-color)] transition-all"
            >
              登录
            </button>
          </template>
          <button 
            @click="openAddModal"
            class="px-4 py-2 rounded-xl bg-[var(--accent-color)] text-white text-sm font-medium hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-[var(--accent-color)]/20">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            添加配队
          </button>
        </div>
      </div>
    </header>

    <CharacterFilter ref="filterRef" @team-change="handleTeamChange">
      <div class="max-w-5xl mx-auto py-6 px-4 flex-1 pb-32">
        <!-- 搜索框和布局切换 -->
        <div class="mb-4 flex items-center gap-3">
          <div class="relative flex-1">
            <input
              v-model="searchQuery"
              @input="handleSearch"
              type="text"
              placeholder="搜索配队名称..."
              class="w-full px-4 py-2.5 pl-10 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/20 transition-all"
            >
            <svg class="w-4 h-4 text-[var(--text-tertiary)] absolute left-3.5 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <button
              v-if="searchQuery"
              @click="searchQuery = ''; handleSearch()"
              class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-[var(--bg-tertiary)] flex items-center justify-center hover:opacity-80 transition-all"
            >
              <svg class="w-3 h-3 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <button
            @click="isGridView = !isGridView"
            class="px-3 py-2.5 rounded-xl bg-[var(--bg-secondary)] border border-[var(--border-color)] text-[var(--text-secondary)] hover:text-[var(--accent-color)] hover:border-[var(--accent-color)] transition-all"
            title="切换布局"
          >
            <svg v-if="!isGridView" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM4 10h16M4 14a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM4 18h16" />
            </svg>
          </button>
        </div>

        <!-- 筛选提示 -->
        <div v-if="selectedCharacterIds.length > 0" class="mb-4 flex items-center justify-between bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-xl px-4 py-2.5">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-[var(--accent-color)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span class="text-xs text-[var(--text-secondary)]">
              已选择 <span class="font-semibold text-[var(--text-primary)]">{{ selectedCharacterIds.length }}</span> 个角色进行筛选
            </span>
          </div>
          <button
            @click="selectedCharacterIds = []; pagination.page = 1; loadTeams()"
            class="text-[10px] text-[var(--accent-color)] hover:opacity-80 transition-opacity"
          >
            清除角色筛选
          </button>
        </div>

        <div v-if="loading" class="flex flex-col items-center justify-center py-20">
          <div class="relative w-12 h-12">
            <div class="absolute inset-0 border-4 border-[var(--border-color)] rounded-full"></div>
            <div class="absolute inset-0 border-4 border-[var(--accent-color)] rounded-full border-t-transparent animate-spin"></div>
          </div>
          <div class="mt-4 text-[var(--text-secondary)] text-sm">加载中...</div>
        </div>
        
        <div v-else-if="teams.length > 0" :class="isGridView ? 'grid grid-cols-1 md:grid-cols-2 gap-4' : 'space-y-4'">
          <TeamCard
            v-for="t in teams"
            :key="t.id"
            :team="t"
            :is-grid-view="isGridView"
            @view="handleViewTeam"
            @edit="handleEditTeam"
            @delete="handleDeleteTeam"
          />
          
          <!-- 分页 -->
          <div v-if="pagination.count > pagination.page_size" class="flex justify-center gap-2 mt-6">
            <button 
              @click="pagination.page--; loadTeams()"
              :disabled="pagination.page <= 1"
              class="px-4 py-2 rounded-xl bg-[var(--bg-secondary)] border border-[var(--border-color)] text-sm disabled:opacity-50 disabled:cursor-not-allowed">
              上一页
            </button>
            <span class="px-4 py-2 text-sm text-[var(--text-secondary)]">
              第 {{ pagination.page }} 页 / 共 {{ Math.ceil(pagination.count / pagination.page_size) }} 页
            </span>
            <button 
              @click="pagination.page++; loadTeams()"
              :disabled="pagination.page * pagination.page_size >= pagination.count"
              class="px-4 py-2 rounded-xl bg-[var(--bg-secondary)] border border-[var(--border-color)] text-sm disabled:opacity-50 disabled:cursor-not-allowed">
              下一页
            </button>
          </div>
        </div>

        <div v-else class="text-center py-20">
          <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-[var(--bg-secondary)] flex items-center justify-center">
            <svg class="w-10 h-10 text-[var(--text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div class="text-[var(--text-secondary)] text-base mb-1">暂无配队</div>
          <div class="text-[var(--text-tertiary)] text-sm">点击右上角添加配队</div>
        </div>
      </div>
    </CharacterFilter>

    <AddTeamModal v-if="showAddModal" @save="saveNewTeam" @close="showAddModal = false" />
    
    <EditTeamModal v-model="showEditModal" :team="currentTeam" @save="saveEditedTeam" @close="showEditModal = false" />
    
    <TeamDetailModal v-model="showDetailModal" :team="currentTeam" />
    
    <AuthModal v-model="showAuthModal" @login-success="onLoginSuccess" />
    
    <!-- Toast 提示 -->
    <div v-if="showToast" class="fixed top-6 left-1/2 -translate-x-1/2 z-50 animate-fade-in-down">
      <div :class="['px-6 py-3 rounded-xl shadow-2xl flex items-center gap-3 border', 
        toastType === 'success' 
          ? 'bg-green-500/95 text-white border-green-400/30' 
          : 'bg-red-500/95 text-white border-red-400/30']">
        <svg v-if="toastType === 'success'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span class="text-sm font-medium">{{ toastMessage }}</span>
      </div>
    </div>
    
    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in">
      <div class="bg-[var(--bg-secondary)] rounded-2xl p-6 w-full max-w-sm mx-4 border border-[var(--border-color)] shadow-2xl animate-scale-in">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-[var(--text-primary)]">确认删除</h3>
        </div>
        <p class="text-[var(--text-secondary)] mb-6">{{ confirmMessage }}</p>
        <div class="flex gap-3">
          <button
            @click="() => { showConfirmDialog = false; confirmCallback = null }"
            class="flex-1 px-4 py-2.5 rounded-xl bg-[var(--bg-tertiary)] text-[var(--text-secondary)] font-medium hover:bg-[var(--bg-primary)] transition-all"
          >
            取消
          </button>
          <button
            @click="() => { if (confirmCallback) confirmCallback() }"
            class="flex-1 px-4 py-2.5 rounded-xl bg-red-500 text-white font-medium hover:bg-red-600 transition-all shadow-lg shadow-red-500/30"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #1d1d1f;
  --bg-tertiary: #2c2c2e;
  --text-primary: #f5f5f7;
  --text-secondary: #98989d;
  --text-tertiary: #636366;
  --border-color: #38383a;
  --accent-color: #ff2d55;
}

html { color-scheme: dark; }

body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }

@keyframes fade-in-down {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

.animate-fade-in-down {
  animation: fade-in-down 0.3s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.2s ease-out;
}

.animate-scale-in {
  animation: scale-in 0.2s ease-out;
}
</style>
