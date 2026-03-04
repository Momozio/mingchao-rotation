<script setup>
import { ref, onMounted } from 'vue'
import CharacterFilter from './components/CharacterFilter.vue'
import AddTeamModal from './components/AddTeamModal.vue'

const team = ref([])
const filterRef = ref(null)
const showAddModal = ref(false)
const teams = ref([])
const nextId = ref(1)

const handleTeamChange = (newTeam) => {
  team.value = newTeam
}

const openAddModal = () => {
  if (filterRef.value) filterRef.value.clearTeamSelection()
  team.value = []
  showAddModal.value = true
}

const saveTeam = (teamData) => {
  teams.value.unshift({ id: nextId.value++, ...teamData })
  showAddModal.value = false
}

const deleteTeam = (id) => {
  teams.value = teams.value.filter(t => t.id !== id)
}

onMounted(() => {
  document.documentElement.classList.add('dark')
})
</script>

<template>
  <div class="h-screen flex flex-col bg-[var(--bg-primary)] overflow-hidden">
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
          class="px-4 py-2 rounded-xl bg-[var(--accent-color)] text-white text-sm font-medium hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-[var(--accent-color)]/20"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          添加配队
        </button>
      </div>
    </header>

    <CharacterFilter ref="filterRef" @team-change="handleTeamChange">
      <div class="max-w-3xl mx-auto py-6 px-4">
        <div v-if="teams.length > 0" class="space-y-4">
          <div 
            v-for="t in teams" 
            :key="t.id"
            class="bg-[var(--bg-secondary)] rounded-2xl shadow-lg border border-[var(--border-color)] p-5 hover:border-[var(--accent-color)]/50 transition-all group"
          >
            <div class="flex items-start justify-between mb-4">
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="text-lg font-semibold text-[var(--text-primary)]">{{ t.name }}</h3>
                  <span class="px-2 py-0.5 rounded-full text-[10px] bg-[var(--accent-color)]/20 text-[var(--accent-color)]">#{{ t.id }}</span>
                </div>
                <p v-if="t.remark" class="text-xs text-[var(--text-tertiary)] mt-1">{{ t.remark }}</p>
              </div>
              <button 
                @click="deleteTeam(t.id)"
                class="p-2 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-500/20 transition-all"
              >
                <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>

            <div class="flex items-center gap-3 mb-4">
              <div v-for="(char, idx) in t.characters" :key="idx" class="flex items-center gap-2">
                <img 
                  :src="`/assets/characters/${char.name}.webp`" 
                  :alt="char.name"
                  class="w-10 h-10 object-contain rounded-lg"
                  @error="$event.target.style.display='none'"
                >
                <div>
                  <div class="text-xs font-medium text-[var(--text-primary)]">{{ char.name }}</div>
                  <div class="flex items-center gap-1">
                    <img :src="`/assets/icons/${char.element}.webp`" class="w-3 h-3 object-contain">
                    <img :src="`/assets/icons/${char.weapon}.webp`" class="w-3 h-3 object-contain">
                    <span v-if="char.energy" class="text-[9px] text-cyan-400">{{ char.energy }}</span>
                  </div>
                </div>
                <span v-if="idx < t.characters.length - 1" class="text-[var(--text-tertiary)]">→</span>
              </div>
            </div>

            <div class="flex flex-wrap gap-2 mb-4">
              <span 
                v-for="env in t.environment" 
                :key="env"
                class="px-2.5 py-1 rounded-lg text-xs font-medium"
                :class="{
                  'bg-green-500/20 text-green-400': env === '通用',
                  'bg-blue-500/20 text-blue-400': env.includes('海虚')
                }"
              >
                {{ env }}
              </span>
            </div>

            <div class="grid grid-cols-3 gap-3 mb-4">
              <div class="bg-[var(--bg-tertiary)] rounded-xl p-3 text-center">
                <div class="text-base font-semibold text-[var(--text-primary)]">{{ t.axisLength || '-' }}<span class="text-xs text-[var(--text-tertiary)]">s</span></div>
                <div class="text-[10px] text-[var(--text-tertiary)]">轴长</div>
              </div>
              <div class="bg-[var(--bg-tertiary)] rounded-xl p-3 text-center">
                <div class="text-base font-semibold text-[var(--text-primary)]">{{ t.dps || '-' }}<span class="text-xs text-[var(--text-tertiary)]">w</span></div>
                <div class="text-[10px] text-[var(--text-tertiary)]">DPS</div>
              </div>
              <div class="bg-[var(--bg-tertiary)] rounded-xl p-3 text-center">
                <div class="text-base font-semibold text-[var(--text-primary)]">{{ t.difficulty }}</div>
                <div class="text-[10px] text-[var(--text-tertiary)]">难度</div>
              </div>
            </div>

            <div v-if="t.flow.startup || t.flow.loop" class="border-t border-[var(--border-color)] pt-4">
              <div class="text-xs font-medium text-[var(--text-secondary)] mb-2">输出流程</div>
              <div v-if="t.flow.startup" class="bg-[var(--bg-tertiary)] rounded-lg p-3 text-sm text-[var(--text-primary)] mb-2">
                <span class="text-[var(--accent-color)]">启动轴：</span>{{ t.flow.startup }}
              </div>
              <div v-if="t.flow.loop" class="bg-[var(--bg-tertiary)] rounded-lg p-3 text-sm text-[var(--text-primary)]">
                <span class="text-[var(--accent-color)]">循环轴：</span>{{ t.flow.loop }}
              </div>
            </div>

            <div class="mt-3 flex items-center justify-between">
              <span class="text-xs text-[var(--text-tertiary)]">贡献者：{{ t.contributors }}</span>
            </div>
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
  </div>
</template>

<style>
:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #1d1d1f;
  --bg-tertiary: #2c2c2e;
  --bg-input: #2c2c2e;
  --text-primary: #f5f5f7;
  --text-secondary: #98989d;
  --text-tertiary: #636366;
  --border-color: #38383a;
  --accent-color: #ff2d55;
  --star-active-bg: #ff9f0a;
  --element-active-bg: #bf5af2;
}

html { color-scheme: dark; }

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  overflow: hidden;
}

select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23636366' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 32px;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

select option {
  background: #1d1d1f !important;
  color: #f5f5f7 !important;
  padding: 14px 18px !important;
  font-size: 14px !important;
  border: none !important;
  outline: none !important;
}

select option:hover,
select option:focus,
select option:checked,
select option:selected {
  background: #ff2d55 !important;
  color: white !important;
}
</style>