<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { teamAPI } from '../services/api'
import TeamCard from './TeamCard.vue'

const authStore = useAuthStore()

const showDropdown = ref(false)
const showMyTeamsModal = ref(false)
const myTeams = ref([])
const loading = ref(false)
const pagination = ref({
  page: 1,
  page_size: 10,
  count: 0
})

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

const openMyTeams = async () => {
  showDropdown.value = false
  showMyTeamsModal.value = true
  pagination.value.page = 1
  await loadMyTeams()
}

const loadMyTeams = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.page_size,
      created_by: authStore.user?.id
    }
    const data = await teamAPI.getTeams(params)
    myTeams.value = data.results || data
    pagination.value.count = data.count || data.length
  } catch (error) {
    console.error('Failed to load my teams:', error)
  } finally {
    loading.value = false
  }
}

const handleViewTeam = (team) => {
  showMyTeamsModal.value = false
  emit('view-team', team)
}

const handleEditTeam = (team) => {
  showMyTeamsModal.value = false
  emit('edit-team', team)
}

const handleDeleteTeam = async (id, createdBy) => {
  const confirmed = confirm('确定要删除这个配队吗？')
  if (!confirmed) return
  
  try {
    await teamAPI.deleteTeam(id)
    await loadMyTeams()
    emit('team-deleted')
  } catch (error) {
    console.error('Failed to delete team:', error)
    alert('删除失败：' + error.message)
  }
}

const emit = defineEmits(['view-team', 'edit-team', 'team-deleted'])
</script>

<template>
  <div class="relative">
    <button
      @click="toggleDropdown"
      @click.stop
      class="flex items-center gap-2 px-3 py-2 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-sm text-[var(--text-secondary)] hover:text-[var(--accent-color)] transition-all"
    >
      <span>{{ authStore.user?.username }}</span>
      <svg 
        :class="['w-4 h-4 transition-transform', showDropdown ? 'rotate-180' : '']" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div 
      v-if="showDropdown" 
      class="absolute right-0 mt-2 w-48 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-xl shadow-lg overflow-hidden z-50"
      @click.stop
    >
      <div class="py-1">
        <button
          @click="openMyTeams"
          class="w-full px-4 py-2.5 text-left text-sm text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4 text-[var(--accent-color)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          我的配队
        </button>
        <div class="border-t border-[var(--border-color)] my-1"></div>
        <button
          @click="authStore.logout()"
          class="w-full px-4 py-2.5 text-left text-sm text-red-400 hover:bg-[var(--bg-tertiary)] transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          退出登录
        </button>
      </div>
    </div>

    <div v-if="showDropdown" class="fixed inset-0 z-40" @click="closeDropdown"></div>

    <!-- 我的配队弹窗 -->
    <div v-if="showMyTeamsModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-black/70 backdrop-blur-sm" @click="showMyTeamsModal = false"></div>
      <div class="relative w-full max-w-4xl bg-[var(--bg-secondary)] rounded-2xl shadow-2xl border border-[var(--border-color)] overflow-hidden max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between p-5 border-b border-[var(--border-color)]">
          <h3 class="text-lg font-semibold text-[var(--text-primary)]">我的配队</h3>
          <button @click="showMyTeamsModal = false" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)] transition-colors">
            <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-5">
          <div v-if="loading" class="flex flex-col items-center justify-center py-20">
            <div class="relative w-12 h-12">
              <div class="absolute inset-0 border-4 border-[var(--border-color)] rounded-full"></div>
              <div class="absolute inset-0 border-4 border-[var(--accent-color)] rounded-full border-t-transparent animate-spin"></div>
            </div>
            <div class="mt-4 text-[var(--text-secondary)] text-sm">加载中...</div>
          </div>

          <div v-else-if="myTeams.length === 0" class="text-center py-20">
            <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-[var(--bg-tertiary)] flex items-center justify-center">
              <svg class="w-10 h-10 text-[var(--text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div class="text-[var(--text-secondary)] text-base mb-1">暂无配队</div>
            <div class="text-[var(--text-tertiary)] text-sm">快去创建第一个配队吧</div>
          </div>

          <div v-else class="space-y-4">
            <TeamCard
              v-for="team in myTeams" 
              :key="team.id"
              :team="team"
              @view="handleViewTeam"
              @edit="handleEditTeam"
              @delete="handleDeleteTeam"
            />

            <!-- 分页 -->
            <div v-if="pagination.count > pagination.page_size" class="flex justify-center gap-2 mt-6">
              <button 
                @click="pagination.page--; loadMyTeams()"
                :disabled="pagination.page <= 1"
                class="px-4 py-2 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一页
              </button>
              <span class="px-4 py-2 text-sm text-[var(--text-secondary)]">
                第 {{ pagination.page }} 页 / 共 {{ Math.ceil(pagination.count / pagination.page_size) }} 页
              </span>
              <button 
                @click="pagination.page++; loadMyTeams()"
                :disabled="pagination.page * pagination.page_size >= pagination.count"
                class="px-4 py-2 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
