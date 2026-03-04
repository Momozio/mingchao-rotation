<script setup>
import { ref, onMounted } from 'vue'
import CharacterFilter from './components/CharacterFilter.vue'

const team = ref([])
const filterRef = ref(null)
const showAddModal = ref(false)
const showCharacterPicker = ref(false)
const teams = ref([])
const nextId = ref(1)
const allCharacters = ref([])
const selectingIndex = ref(null)

const handleTeamChange = (newTeam) => {
  team.value = newTeam
}

const newTeam = ref({
  name: '',
  remark: '',
  axisLength: '',
  dps: '',
  matrixScore: '',
  difficulty: '中等',
  environment: ['通用'],
  flow: {
    startup: '',
    loop: ''
  },
  contributors: 'mozz',
  characters: []
})

const environments = ['通用', '海虚满协奏']
const difficulties = ['简单', '中等', '困难']

const toggleEnvironment = (env) => {
  const idx = newTeam.value.environment.indexOf(env)
  if (idx > -1) {
    newTeam.value.environment.splice(idx, 1)
  } else {
    newTeam.value.environment = [env]
  }
}

const calculateDPS = (event) => {
  const value = event.target.value.replace(/[^\d.]/g, '')
  newTeam.value.dps = value
  if (value) {
    const num = parseFloat(value)
    if (!isNaN(num)) {
      newTeam.value.matrixScore = Math.round(num * 1200 * 100) / 100
    }
  }
}

const calculateMatrix = (event) => {
  const value = event.target.value.replace(/[^\d.]/g, '')
  newTeam.value.matrixScore = value
  if (value) {
    const num = parseFloat(value)
    if (!isNaN(num)) {
      newTeam.value.dps = (num / 1200).toFixed(2)
    }
  }
}

const fetchCharacters = async () => {
  try {
    const res = await fetch('/api/characters/')
    allCharacters.value = await res.json()
  } catch (e) {
    console.error('Failed to fetch characters:', e)
  }
}

const openAddModal = () => {
  if (filterRef.value) {
    filterRef.value.clearTeamSelection()
  }
  team.value = []
  
  newTeam.value.characters = [
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' },
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' },
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' }
  ]
  
  fetchCharacters()
  showAddModal.value = true
}

const openCharacterPicker = (index) => {
  selectingIndex.value = index
  showCharacterPicker.value = true
}

const selectCharacter = (char) => {
  newTeam.value.characters[selectingIndex.value] = {
    id: char.id,
    name: char.name,
    star: char.star,
    weapon: char.weapon,
    element: char.element,
    energy: ''
  }
  showCharacterPicker.value = false
  selectingIndex.value = null
}

const removeCharacter = (index) => {
  newTeam.value.characters[index] = { id: null, name: null, star: null, weapon: null, element: null, energy: '' }
}

const handleEnergyInput = (char, event) => {
  let value = event.target.value.replace(/[^\d%]/g, '')
  if (value && !value.endsWith('%')) {
    value = value.replace('%', '') + '%'
  }
  char.energy = value
}

const saveTeam = () => {
  if (!newTeam.value.name.trim()) {
    alert('请输入配队名称')
    return
  }
  
  const selectedChars = newTeam.value.characters.filter(c => c.id !== null)
  if (selectedChars.length === 0) {
    alert('请至少选择1名角色')
    return
  }
  
  const teamData = {
    id: nextId.value++,
    name: newTeam.value.name,
    remark: newTeam.value.remark,
    axisLength: newTeam.value.axisLength,
    dps: newTeam.value.dps,
    difficulty: newTeam.value.difficulty,
    environment: newTeam.value.environment,
    flow: newTeam.value.flow,
    contributors: newTeam.value.contributors,
    characters: newTeam.value.characters.filter(c => c.id !== null)
  }
  
  teams.value.unshift(teamData)
  showAddModal.value = false
  
  newTeam.value = {
    name: '',
    remark: '',
    axisLength: '',
    dps: '',
    matrixScore: '',
    difficulty: '中等',
    environment: ['通用'],
    flow: { startup: '', loop: '' },
    contributors: 'mozz',
    characters: []
  }
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
            鸣潮排轴工具
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
            class="bg-[var(--bg-secondary)] rounded-2xl shadow-lg border border-[var(--border-color)] p-5 hover:border-[var(--accent-color)]/50 transition-all"
          >
            <div class="flex items-start justify-between mb-4">
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="text-lg font-semibold text-[var(--text-primary)]">{{ t.name }}</h3>
                  <span class="px-2 py-0.5 rounded-full text-[10px] bg-[var(--accent-color)]/20 text-[var(--accent-color)]">#{{ t.id }}</span>
                </div>
                <p v-if="t.remark" class="text-xs text-[var(--text-tertiary)] mt-1">{{ t.remark }}</p>
              </div>
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

    <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70" @click="showAddModal = false"></div>
      <div class="relative w-full max-w-2xl bg-[var(--bg-secondary)] rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col border border-[var(--border-color)]">
        <div class="flex items-center justify-between p-5 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]/30">
          <h2 class="text-lg font-semibold text-[var(--text-primary)]">添加配队</h2>
          <button @click="showAddModal = false" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)] transition-colors">
            <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-5">
          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">配队名称 <span class="text-red-400">*</span></label>
            <input 
              v-model="newTeam.name"
              type="text" 
              placeholder="输入配队名称"
              class="w-full px-4 py-3 bg-[var(--bg-tertiary)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 focus:border-[var(--accent-color)] transition-all"
            >
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">备注（可选）</label>
            <input 
              v-model="newTeam.remark"
              type="text" 
              placeholder="补充说明"
              class="w-full px-4 py-3 bg-[var(--bg-tertiary)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 focus:border-[var(--accent-color)] transition-all"
            >
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">选择角色 <span class="text-red-400">*</span></label>
            <div class="flex justify-center gap-4 mb-3">
              <div
                v-for="(char, index) in newTeam.characters"
                :key="index"
                class="w-28"
              >
                <div 
                  v-if="char.id"
                  class="relative group"
                >
                  <div class="aspect-square rounded-2xl bg-[var(--bg-tertiary)] border-2 border-[var(--accent-color)] flex flex-col items-center justify-center p-2 overflow-hidden">
                    <img 
                      :src="`/assets/characters/${char.name}.webp`" 
                      :alt="char.name"
                      class="w-16 h-16 object-contain"
                      @error="$event.target.style.display='none'"
                    >
                    <span class="text-[10px] text-[var(--text-primary)] truncate w-full text-center">{{ char.name }}</span>
                  </div>
                  <button 
                    @click="removeCharacter(index)"
                    class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  <input 
                    v-model="char.energy"
                    @input="handleEnergyInput(char, $event)"
                    type="text"
                    placeholder="默认无需求"
                    class="w-full mt-2 px-2 py-1.5 bg-[var(--bg-tertiary)] rounded-lg text-xs text-[var(--text-primary)] text-center"
                  >
                  <div class="text-[10px] text-cyan-400 text-center mt-0.5">充能需求</div>
                </div>
                <div
                  v-else
                  @click="openCharacterPicker(index)"
                  class="aspect-square rounded-2xl border-2 border-dashed border-[var(--border-color)] flex items-center justify-center cursor-pointer hover:border-[var(--accent-color)] hover:bg-[var(--bg-tertiary)] transition-all bg-[var(--bg-tertiary)]/50"
                >
                  <span class="text-sm text-[var(--text-tertiary)]">+ 选择</span>
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">适配环境</label>
            <div class="flex gap-2">
              <button
                v-for="env in environments"
                :key="env"
                @click="toggleEnvironment(env)"
                class="flex-1 py-2.5 rounded-xl text-sm font-medium transition-all"
                :class="newTeam.environment.includes(env)
                  ? 'bg-[var(--accent-color)] text-white shadow-lg shadow-[var(--accent-color)]/20'
                  : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]/80'"
              >
                {{ env }}
              </button>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-sm text-[var(--text-secondary)] mb-2">轴长(s)</label>
              <input 
                v-model="newTeam.axisLength"
                type="text" 
                placeholder="20"
                class="w-full px-3 py-2.5 bg-[var(--bg-tertiary)] rounded-xl text-sm text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30"
              >
            </div>
            <div>
              <label class="block text-sm text-[var(--text-secondary)] mb-2">DPS(w) / 矩阵分数</label>
              <div class="space-y-2">
                <input 
                  v-model="newTeam.dps"
                  @input="calculateDPS"
                  type="text" 
                  placeholder="DPS"
                  class="w-full px-2 py-2 bg-[var(--bg-tertiary)] rounded-lg text-xs text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30"
                >
                <input 
                  v-model="newTeam.matrixScore"
                  @input="calculateMatrix"
                  type="text" 
                  placeholder="矩阵"
                  class="w-full px-2 py-2 bg-[var(--bg-tertiary)] rounded-lg text-xs text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30"
                >
              </div>
              <div class="text-[9px] text-[var(--text-tertiary)] mt-1 text-center">DPS = 矩阵 ÷ 1200</div>
            </div>
            <div>
              <label class="block text-sm text-[var(--text-secondary)] mb-2">难度</label>
              <div class="relative">
                <select 
                  v-model="newTeam.difficulty"
                  class="w-full px-3 py-2.5 bg-[var(--bg-tertiary)] rounded-xl text-sm text-[var(--text-primary)] text-center appearance-none focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 cursor-pointer"
                >
                  <option v-for="d in difficulties" :key="d" :value="d">{{ d }}</option>
                </select>
                <svg class="w-4 h-4 text-[var(--text-tertiary)] absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">启动轴</label>
            <textarea 
              v-model="newTeam.flow.startup"
              placeholder="角色A开E→角色B QTE→角色C E..."
              rows="2"
              class="w-full px-4 py-3 bg-[var(--bg-tertiary)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">循环轴</label>
            <textarea 
              v-model="newTeam.flow.loop"
              placeholder="角色A AAZ→角色B QTE→..."
              rows="2"
              class="w-full px-4 py-3 bg-[var(--bg-tertiary)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">贡献者</label>
            <input 
              v-model="newTeam.contributors"
              type="text" 
              placeholder="贡献者"
              class="w-full px-4 py-3 bg-[var(--bg-tertiary)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30"
            >
          </div>
        </div>

        <div class="p-5 border-t border-[var(--border-color)] flex gap-3 bg-[var(--bg-tertiary)]/30">
          <button 
            @click="showAddModal = false"
            class="flex-1 py-3 rounded-xl bg-[var(--bg-tertiary)] text-[var(--text-primary)] font-medium text-sm hover:opacity-80 transition-all"
          >
            取消
          </button>
          <button 
            @click="saveTeam"
            class="flex-1 py-3 rounded-xl bg-[var(--accent-color)] text-white font-medium text-sm hover:opacity-90 transition-all shadow-lg shadow-[var(--accent-color)]/20"
          >
            保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCharacterPicker" class="fixed inset-0 z-60 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70" @click="showCharacterPicker = false"></div>
      <div class="relative w-full max-w-3xl bg-[var(--bg-secondary)] rounded-2xl shadow-2xl overflow-hidden max-h-[80vh] flex flex-col border border-[var(--border-color)]">
        <div class="flex items-center justify-between p-4 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]/30">
          <h2 class="text-lg font-semibold text-[var(--text-primary)]">选择角色</h2>
          <button @click="showCharacterPicker = false" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)]">
            <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <div class="grid grid-cols-5 gap-3">
            <div
              v-for="char in allCharacters"
              :key="char.id"
              @click="selectCharacter(char)"
              class="rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--accent-color)]/20 border-2 border-transparent hover:border-[var(--accent-color)] cursor-pointer transition-all flex flex-col items-center justify-center p-3 overflow-hidden"
            >
              <img 
                :src="`/assets/characters/${char.name}.webp`" 
                :alt="char.name"
                class="w-14 h-14 object-contain mb-1.5"
                @error="$event.target.style.display='none'"
              >
              <span class="text-[10px] text-[var(--text-primary)] text-center truncate w-full">{{ char.name }}</span>
              <div class="flex items-center gap-1 mt-1">
                <img :src="`/assets/icons/${char.element}.webp`" class="w-3.5 h-3.5 object-contain">
                <img :src="`/assets/icons/${char.weapon}.webp`" class="w-3.5 h-3.5 object-contain">
                <span :class="char.star === 5 ? 'text-amber-400' : 'text-purple-400'" class="text-[8px]">★</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
:root {
  --bg-primary: #000000;
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
  background: #000000;
  overflow: hidden;
}

option {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: 8px;
}
</style>