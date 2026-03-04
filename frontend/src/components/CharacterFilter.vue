<script setup>
import { ref, onMounted, computed } from 'vue'

const emit = defineEmits(['team-change'])

const allCharacters = ref([])
const filterOptions = ref({
  stars: [],
  weapons: [],
  elements: []
})

const selectedFilters = ref({
  stars: [],
  weapons: [],
  elements: [],
  search: ''
})

const team = ref([])
const isCollapsed = ref(false)
const isSearchOpen = ref(false)

const fetchData = async () => {
  try {
    const [charsRes, optionsRes] = await Promise.all([
      fetch('/api/characters/'),
      fetch('/api/filter-options/')
    ])
    allCharacters.value = await charsRes.json()
    const options = await optionsRes.json()
    filterOptions.value = {
      stars: options.stars,
      weapons: options.weapons,
      elements: options.elements
    }
  } catch (e) {
    console.error('Failed to load data:', e)
  }
}

const filteredCharacters = computed(() => {
  let result = allCharacters.value
  
  if (selectedFilters.value.search) {
    const search = selectedFilters.value.search.toLowerCase()
    result = result.filter(c => 
      c.name.toLowerCase().includes(search) || 
      (c.pinyin && c.pinyin.toLowerCase().includes(search)) ||
      (c.abbr && c.abbr.toLowerCase().includes(search))
    )
  }
  if (selectedFilters.value.stars.length > 0) {
    result = result.filter(c => selectedFilters.value.stars.includes(c.star))
  }
  if (selectedFilters.value.weapons.length > 0) {
    result = result.filter(c => selectedFilters.value.weapons.includes(c.weapon))
  }
  if (selectedFilters.value.elements.length > 0) {
    result = result.filter(c => selectedFilters.value.elements.includes(c.element))
  }
  
  return result
})

const toggleCharacter = (char) => {
  const idx = team.value.findIndex(c => c.id === char.id)
  if (idx > -1) {
    team.value.splice(idx, 1)
    emit('team-change', [...team.value])
  } else if (team.value.length < 3) {
    team.value.push(char)
    emit('team-change', [...team.value])
  }
}

const removeFromTeam = (index) => {
  team.value.splice(index, 1)
  emit('team-change', [...team.value])
}

const clearTeam = () => {
  team.value = []
  emit('team-change', [])
}

const toggleStar = (star) => {
  const idx = selectedFilters.value.stars.indexOf(star)
  if (idx > -1) {
    selectedFilters.value.stars.splice(idx, 1)
  } else {
    selectedFilters.value.stars.push(star)
  }
}

const toggleWeapon = (weapon) => {
  const idx = selectedFilters.value.weapons.indexOf(weapon)
  if (idx > -1) {
    selectedFilters.value.weapons.splice(idx, 1)
  } else {
    selectedFilters.value.weapons.push(weapon)
  }
}

const toggleElement = (element) => {
  const idx = selectedFilters.value.elements.indexOf(element)
  if (idx > -1) {
    selectedFilters.value.elements.splice(idx, 1)
  } else {
    selectedFilters.value.elements.push(element)
  }
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const getAvatarUrl = (name) => `/assets/characters/${name}.webp`
const getIconUrl = (name) => `/assets/icons/${name}.webp`

const clearTeamSelection = () => {
  team.value = []
}

onMounted(() => {
  fetchData()
})

defineExpose({ team, clearTeamSelection })
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex flex-1 overflow-hidden">
      <aside
        class="bg-[var(--bg-secondary)] border-r border-[var(--border-color)] flex flex-col transition-all duration-300 overflow-hidden"
        :class="isCollapsed ? 'w-0' : 'w-80'"
      >
        <div v-show="!isCollapsed" class="h-full flex flex-col overflow-hidden p-4 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-semibold text-[var(--text-primary)]">当前筛选</h2>
            <div class="flex items-center gap-1.5">
              <button
                @click="isSearchOpen = !isSearchOpen"
                class="w-8 h-8 rounded-lg bg-[var(--bg-tertiary)] flex items-center justify-center hover:opacity-80 transition-all"
              >
                <svg class="w-4 h-4 text-[var(--text-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
              <button
                @click="clearTeam"
                class="w-8 h-8 rounded-lg bg-[var(--bg-tertiary)] flex items-center justify-center hover:opacity-80 transition-all"
                title="清空"
              >
                <svg class="w-4 h-4 text-[var(--accent-color)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <div v-if="isSearchOpen" class="relative">
            <input
              v-model="selectedFilters.search"
              type="text"
              placeholder="搜索角色..."
              class="w-full px-3 py-2 pl-9 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/20"
            >
            <svg class="w-4 h-4 text-[var(--text-tertiary)] absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          <div class="flex gap-2">
            <div
              v-for="(char, index) in team"
              :key="char.id"
              class="flex-1 relative group cursor-pointer"
              @click="removeFromTeam(index)"
            >
              <div class="aspect-square rounded-2xl bg-[var(--bg-tertiary)] shadow-lg border-2 border-[var(--accent-color)] flex flex-col items-center justify-center p-2 overflow-hidden">
                <img 
                  :src="getAvatarUrl(char.name)" 
                  :alt="char.name"
                  class="w-10 h-10 object-contain mb-0.5"
                  @error="$event.target.style.display='none'"
                >
                <span class="text-[9px] text-[var(--text-primary)] truncate w-full text-center leading-tight">{{ char.name }}</span>
                <div class="flex items-center gap-0.5 mt-0.5">
                  <img :src="getIconUrl(char.element)" class="w-2.5 h-2.5 object-contain">
                  <img :src="getIconUrl(char.weapon)" class="w-2.5 h-2.5 object-contain">
                </div>
              </div>
              <div class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-10">
                <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
            </div>
            <div
              v-for="i in (3 - team.length)"
              :key="i"
              class="flex-1"
            >
              <div class="aspect-square rounded-2xl border-2 border-dashed border-[var(--border-color)] flex items-center justify-center">
                <span class="text-xs text-[var(--text-tertiary)]">空位</span>
              </div>
            </div>
          </div>

          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-2">星级</label>
              <div class="flex gap-1.5">
                <button
                  v-for="star in filterOptions.stars"
                  :key="star"
                  @click="toggleStar(star)"
                  class="flex-1 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-1"
                  :class="selectedFilters.stars.includes(star)
                    ? star === 5 ? 'bg-amber-400 text-white shadow-lg' : 'bg-purple-500 text-white shadow-lg'
                    : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:opacity-80'"
                >
                  <span>{{ star }}星</span>
                  <span>★</span>
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-2">武器</label>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="weapon in filterOptions.weapons"
                  :key="weapon"
                  @click="toggleWeapon(weapon)"
                  class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-1.5"
                  :class="selectedFilters.weapons.includes(weapon)
                    ? 'bg-[var(--accent-color)] text-white shadow-lg'
                    : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:opacity-80'"
                >
                  <img :src="getIconUrl(weapon)" class="w-4 h-4 object-contain">
                  <span>{{ weapon }}</span>
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-2">元素</label>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="element in filterOptions.elements"
                  :key="element"
                  @click="toggleElement(element)"
                  class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-1.5"
                  :class="selectedFilters.elements.includes(element)
                    ? 'bg-[var(--element-active-bg)] text-white shadow-lg'
                    : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:opacity-80'"
                >
                  <img :src="getIconUrl(element)" class="w-4 h-4 object-contain">
                  <span>{{ element }}</span>
                </button>
              </div>
            </div>
          </div>

          <div class="flex-1 overflow-y-auto min-h-0">
            <div class="grid grid-cols-3 gap-2">
              <div
                v-for="char in filteredCharacters"
                :key="char.id"
                @click="toggleCharacter(char)"
                class="rounded-xl p-2 cursor-pointer transition-all flex flex-col items-center justify-center overflow-hidden relative"
                :class="team.find(c => c.id === char.id)
                  ? 'bg-[var(--accent-color)]/10 border-2 border-[var(--accent-color)]'
                  : 'bg-[var(--bg-tertiary)] hover:opacity-80 border-2 border-transparent'"
              >
                <div 
                  class="absolute top-1 right-1 text-xs font-bold"
                  :class="char.star === 5 ? 'text-amber-400' : 'text-purple-400'"
                >
                  ★
                </div>
                <img 
                  :src="getAvatarUrl(char.name)" 
                  :alt="char.name"
                  class="w-10 h-10 object-contain mb-1"
                  @error="$event.target.style.display='none'"
                >
                <span class="text-[9px] text-[var(--text-primary)] text-center leading-tight truncate w-full">{{ char.name }}</span>
                <div class="flex items-center gap-1 mt-0.5">
                  <img :src="getIconUrl(char.element)" class="w-3 h-3 object-contain">
                  <img :src="getIconUrl(char.weapon)" class="w-3 h-3 object-contain">
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <button
        @click="toggleCollapse"
        class="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-5 h-14 bg-[var(--bg-secondary)] border border-[var(--border-color)] flex items-center justify-center hover:opacity-80 transition-all rounded-r-lg"
        :class="isCollapsed ? 'left-0' : 'left-80'"
      >
        <svg class="w-3 h-3 text-[var(--text-primary)] transition-transform duration-300" :class="{ 'rotate-180': isCollapsed }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <main class="flex-1 overflow-y-auto p-5">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<style scoped>
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 2px; }
</style>