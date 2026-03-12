<script setup>
import { ref, onMounted } from 'vue'
import CharacterFilter from './components/CharacterFilter.vue'
import AddTeamModal from './components/AddTeamModal.vue'
import TeamCard from './components/TeamCard.vue'
import TeamDetailModal from './components/TeamDetailModal.vue'
import TestAction from './components/TestAction.vue'
import TestEditAction from './components/TestEditAction.vue'
import { teamAPI } from './services/api'

const team = ref([])
const filterRef = ref(null)
const showAddModal = ref(false)
const showDetailModal = ref(false)
const currentTeam = ref(null)
const teams = ref([])
const loading = ref(false)
const pagination = ref({
  page: 1,
  page_size: 10,
  count: 0
})

// 加载配队列表
const loadTeams = async () => {
  loading.value = true
  try {
    const data = await teamAPI.getTeams({
      page: pagination.value.page,
      page_size: pagination.value.page_size
    })
    teams.value = data.results || data
    pagination.value.count = data.count || data.length
  } catch (error) {
    console.error('Failed to load teams:', error)
  } finally {
    loading.value = false
  }
}

const handleTeamChange = (newTeam) => {
  team.value = newTeam
}

const openAddModal = () => {
  if (filterRef.value) filterRef.value.clearTeamSelection()
  team.value = []
  showAddModal.value = true
}

const saveTeam = async (teamData) => {
  try {
    const apiData = {
      name: teamData.name,
      remark: teamData.remark || '',
      axis_length: teamData.axisLength ? parseInt(teamData.axisLength) : null,
      dps: teamData.dps ? parseInt(teamData.dps) : null,
      difficulty: teamData.difficulty,
      environment: teamData.environment,
      contributors: teamData.contributors,
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

const deleteTeam = async (id) => {
  if (!confirm('确定要删除这个配队吗？')) return
  try {
    await teamAPI.deleteTeam(id)
    await loadTeams()
  } catch (error) {
    console.error('Failed to delete team:', error)
    alert('删除失败：' + error.message)
  }
}

const handleViewDetail = (t) => {
  currentTeam.value = t
  showDetailModal.value = true
}

onMounted(async () => {
  document.documentElement.classList.add('dark')
  await loadTeams()
})
</script>

<template>
  <div class="h-screen flex flex-col bg-[var(--bg-primary)] overflow-hiddenpb-56">
    <header class="flex-shrink-0 bg-[var(--bg-secondary)] shadow-sm border-b border-[var(--border-color)]">
      <div class="container mx-auto px-5 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-[var(--accent-color)] flex items-center justify-center">
            <span class="text-white text-sm font-bold">鸣</span>
          </div>
          <h1 class="text-lg font-semibold text-[var(--text-primary)]">
            排轴工具
          </h1>
        </div>
        <button 
          @click="openAddModal"
          class="px-4 py-2 rounded-xl bg-[var(--accent-color)] text-white text-sm font-medium hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-[var(--accent-color)]/20">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          添加配队
        </button>
      </div>
    </header>

    <CharacterFilter ref="filterRef" @team-change="handleTeamChange">
      <div class="max-w-5xl mx-auto py-6 px-4 flex-1 overflow-y-auto pb-32">
        <div v-if="loading" class="text-center py-20">
          <div class="text-[var(--text-secondary)]">加载中...</div>
        </div>
        
        <div v-else-if="teams.length > 0" class="space-y-4 ">
          <TeamCard
            v-for="t in teams"
            :key="t.id"
            :team="t"
            @view="handleViewDetail"
            @delete="deleteTeam"
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

    <AddTeamModal v-if="showAddModal" @save="saveTeam" @close="showAddModal = false" />
    
    <TeamDetailModal v-model="showDetailModal" :team="currentTeam" />
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

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  overflow: hidden;
}
</style>
