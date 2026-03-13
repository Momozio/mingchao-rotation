<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, RadioGroup, RadioGroupOption, Listbox, ListboxButton, ListboxOptions, ListboxOption } from '@headlessui/vue'
import RotationEdit from './RotationEdit.vue'
import RotationPlayer from './RotationPlayer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const props = defineProps({
  modelValue: Boolean,
  team: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'close', 'update:modelValue'])

const environments = ['通用', '海虚满协奏']
const difficulties = ['简单', '中等', '困难']

const allCharacters = ref([])
const selectingIndex = ref(null)
const showCharacterPicker = ref(false)
const showAlert = ref(false)
const alertMessage = ref('')

const showAxisEditor = ref(false)
const editingAxisIndex = ref(-1)
const showAxisNameDropdown = ref(false)
const axisForm = ref({
  name: '',
  videoUrl: null,
  rotationData: null
})

const editTeam = ref({
  name: '',
  remark: '',
  axisLength: '',
  dps: '',
  difficulty: '中等',
  environment: '通用',
  characters: [
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' },
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' },
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' }
  ],
  axes: []
})

const quickAxisNames = ['启动轴', '循环轴']

const selectedCharNames = computed(() => {
  return editTeam.value.characters.filter(c => c.name !== null).map(c => c.name)
})

const canAddAxis = computed(() => {
  return selectedCharNames.value.length > 0
})

const handleAxisNameBlur = () => {
  setTimeout(() => { showAxisNameDropdown.value = false }, 150)
}

const calculateDPS = (event) => {
  editTeam.value.dps = event.target.value.replace(/[^\d.]/g, '')
}

const fetchCharacters = async () => {
  try {
    const res = await fetch('/api/characters/')
    allCharacters.value = await res.json()
  } catch (e) { console.error('Failed to fetch:', e) }
}

const openCharacterPicker = (index) => {
  selectingIndex.value = index
  showCharacterPicker.value = true
  if (allCharacters.value.length === 0) fetchCharacters()
}

const selectCharacter = (char) => {
  if (editTeam.value.characters.some(c => c.id === char.id)) {
    alertMessage.value = '该角色已在配队中'
    showAlert.value = true
    return
  }
  editTeam.value.characters[selectingIndex.value] = {
    id: char.id, name: char.name, star: char.star, weapon: char.weapon, element: char.element, energy: ''
  }
  showCharacterPicker.value = false
  selectingIndex.value = null
}

const removeCharacter = (index) => {
  editTeam.value.characters[index] = { id: null, name: null, star: null, weapon: null, element: null, energy: '' }
  editTeam.value.axes = []
}

watch(() => editTeam.value.characters, () => { editTeam.value.axes = [] }, { deep: true })

// 监听传入的 team 数据，加载到表单
watch(() => props.team, (team) => {
  if (team) {
    editTeam.value.name = team.name
    editTeam.value.remark = team.remark || ''
    editTeam.value.axisLength = team.axis_length?.toString() || ''
    editTeam.value.dps = team.dps?.toString() || ''
    editTeam.value.difficulty = team.difficulty || '中等'
    editTeam.value.environment = team.environment || '通用'
    
    // 加载角色
    const chars = team.team_characters || []
    editTeam.value.characters = [
      ...chars.map(c => ({
        id: c.character_id,
        name: c.character_name,
        star: null,
        weapon: null,
        element: null,
        energy: c.energy || ''
      })),
      ...Array(3 - chars.length).fill({ id: null, name: null, star: null, weapon: null, element: null, energy: '' })
    ]
    
    // 加载轴
    editTeam.value.axes = (team.axes || []).map(axis => ({
      name: axis.name,
      videoUrl: axis.video_url,
      rotationData: {
        totalDuration: axis.total_duration,
        characters: axis.characters || [],
        segments: axis.segments_data || {}
      }
    }))
  }
}, { immediate: true })

const handleEnergyInput = (char, event) => {
  let value = event.target.value.replace(/[^\d%]/g, '')
  if (value && !value.endsWith('%')) value = value.replace('%', '') + '%'
  char.energy = value
}

const openAxisEditor = () => {
  if (!canAddAxis.value) {
    alertMessage.value = '请至少选择 1 名角色才能添加轴'
    showAlert.value = true
    return
  }
  editingAxisIndex.value = -1
  axisForm.value = { name: '', videoUrl: null, rotationData: null }
  showAxisEditor.value = true
}

const editAxis = (index) => {
  editingAxisIndex.value = index
  const axis = editTeam.value.axes[index]
  axisForm.value = { name: axis.name, videoUrl: axis.videoUrl, rotationData: axis.rotationData }
  showAxisEditor.value = true
}

const deleteAxis = (index) => {
  editTeam.value.axes.splice(index, 1)
}

const saveAxis = (rotationData) => {
  const axisData = {
    name: axisForm.value.name || '未命名轴',
    videoUrl: rotationData.videoUrl || null,
    rotationData: {
      totalDuration: rotationData.totalDuration,
      characters: rotationData.characters,
      segments: {}
    }
  }
  rotationData.characters.forEach(char => { axisData.rotationData.segments[char.name] = char.segments || [] })
  
  if (editingAxisIndex.value >= 0) {
    editTeam.value.axes[editingAxisIndex.value] = axisData
  } else {
    editTeam.value.axes.push(axisData)
  }
  showAxisEditor.value = false
}

const cancelAxisEdit = () => { showAxisEditor.value = false }

const collapsedAxes = ref({})
const toggleAxisCollapse = (index) => { collapsedAxes.value[index] = !collapsedAxes.value[index] }

const getAxisRotation = (axis) => {
  if (!axis.rotationData) return null
  return {
    name: axis.name,
    totalDuration: axis.rotationData.totalDuration,
    characters: axis.rotationData.characters.map(char => ({ name: char.name, segments: axis.rotationData.segments[char.name] || [] }))
  }
}

const axisCurrentTimes = ref({})
const handleAxisSeek = (axisIndex, time) => { axisCurrentTimes.value[axisIndex] = time }

watch(() => editTeam.value.axes.length, (newLength) => {
  for (let i = 0; i < newLength; i++) {
    if (collapsedAxes.value[i] === undefined) collapsedAxes.value[i] = false
  }
})

const saveTeam = () => {
  if (!editTeam.value.name.trim()) {
    alertMessage.value = '请输入配队名称'
    showAlert.value = true
    return
  }
  const selectedChars = editTeam.value.characters.filter(c => c.id !== null)
  if (selectedChars.length === 0) {
    alertMessage.value = '请至少选择 1 名角色'
    showAlert.value = true
    return
  }
  if (editTeam.value.axes.length === 0) {
    alertMessage.value = '请至少添加 1 个输出轴'
    showAlert.value = true
    return
  }
  const dpsValue = editTeam.value.dps ? Math.round(parseFloat(editTeam.value.dps) * 10000) : ''
  emit('save', { 
    ...editTeam.value, 
    dps: dpsValue, 
    characters: selectedChars,
    id: props.team?.id
  })
}

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

onMounted(() => fetchCharacters())
</script>

<template>
  <Dialog :open="modelValue" @close="close" class="relative z-50">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-black/60"></div>
      <DialogPanel class="relative w-full max-w-4xl bg-[var(--bg-secondary)] rounded-2xl shadow-2xl border border-[var(--border-color)] overflow-hidden max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between p-5 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]/30">
          <DialogTitle class="text-lg font-semibold text-[var(--text-primary)]">编辑配队</DialogTitle>
          <button @click="close" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)] transition-colors">
            <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-5 space-y-5 max-h-[70vh] overflow-y-auto">
          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">配队名称 <span class="text-red-400">*</span></label>
            <input v-model="editTeam.name" type="text" placeholder="输入配队名称"
              class="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">备注</label>
            <input v-model="editTeam.remark" type="text" placeholder="补充说明"
              class="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">选择角色 <span class="text-red-400">*</span></label>
            <div class="relative">
              <div class="flex justify-center gap-4">
                <div v-for="(char, index) in editTeam.characters" :key="index" class="w-28">
                  <div v-if="char.id" class="relative group">
                    <div class="aspect-square rounded-2xl bg-[var(--bg-tertiary)] border-2 border-[var(--accent-color)] flex flex-col items-center justify-center p-2 overflow-hidden">
                      <img :src="`/assets/characters/${char.name}.webp`" :alt="char.name" class="w-16 h-16 object-contain" @error="$event.target.style.display = 'none'">
                      <span class="text-[10px] text-[var(--text-primary)] truncate w-full text-center">{{ char.name }}</span>
                    </div>
                    <button @click="removeCharacter(index)" class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <div v-else @click="openCharacterPicker(index)" class="aspect-square rounded-2xl border-2 border-dashed border-[var(--border-color)] flex items-center justify-center cursor-pointer hover:border-[var(--accent-color)] hover:bg-[var(--bg-tertiary)] transition-all bg-[var(--bg-tertiary)]/50">
                    <span class="text-sm text-[var(--text-tertiary)]">+ 选择</span>
                  </div>
                </div>
              </div>
              <div class="flex justify-center gap-4 mt-3 relative">
                <div class="absolute left-[10rem]" v-if="editTeam.characters.some(c => c.id)">
                  <span class="text-[10px] text-cyan-500 font-medium">充能需求</span>
                </div>
                <div v-for="(char, index) in editTeam.characters" :key="index" class="w-28">
                  <input v-if="char.id" v-model="char.energy" @input="handleEnergyInput(char, $event)" type="text" placeholder="无"
                    class="w-full px-2 py-1.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-lg text-xs text-[var(--text-primary)] text-center">
                </div>
              </div>
            </div>
          </div>

          <div class="border-t border-[var(--border-color)] pt-4">
            <div class="flex items-center justify-between mb-3">
              <label class="block text-sm text-[var(--text-secondary)]">输出轴</label>
              <button @click="openAxisEditor" :disabled="!canAddAxis"
                :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2', canAddAxis ? 'bg-[var(--accent-color)] text-white hover:opacity-90' : 'bg-[var(--bg-tertiary)] text-[var(--text-tertiary)] cursor-not-allowed']">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                添加轴
              </button>
            </div>

            <div v-if="editTeam.axes.length > 0" class="space-y-3">
              <div v-for="(axis, index) in editTeam.axes" :key="index" class="bg-[var(--bg-tertiary)] rounded-xl border border-[var(--border-color)] overflow-hidden">
                <div class="flex items-center justify-between p-3 bg-[var(--bg-tertiary)]/50">
                  <div class="flex items-center gap-3">
                    <button @click="toggleAxisCollapse(index)" class="p-1 rounded hover:bg-[var(--bg-secondary)] transition-colors">
                      <svg :class="['w-4 h-4 text-[var(--text-secondary)] transition-transform', collapsedAxes[index] ? '' : 'rotate-90']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                    <span class="text-sm font-medium text-[var(--text-primary)]">{{ axis.name }}</span>
                    <span class="text-xs text-[var(--text-tertiary)]">{{ axis.rotationData?.totalDuration || 0 }}s</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <button @click="editAxis(index)" class="px-2 py-1 rounded text-xs bg-[var(--accent-color)]/20 text-[var(--accent-color)] hover:bg-[var(--accent-color)]/30 transition-colors">编辑</button>
                    <button @click="deleteAxis(index)" class="px-2 py-1 rounded text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors">删除</button>
                  </div>
                </div>
                <div v-show="!collapsedAxes[index]" class="p-4 border-t border-[var(--border-color)]">
                  <RotationPlayer v-if="getAxisRotation(axis)" :rotation="getAxisRotation(axis)" :current-time="axisCurrentTimes[index] || 0" @seek="(time) => handleAxisSeek(index, time)" />
                </div>
              </div>
            </div>

            <div v-else class="text-center py-6 border-2 border-dashed border-[var(--border-color)] rounded-xl">
              <div class="text-sm text-[var(--text-tertiary)]">{{ canAddAxis ? '点击"添加轴"按钮创建输出轴' : '请先选择角色' }}</div>
            </div>
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">适配环境</label>
            <RadioGroup v-model="editTeam.environment" class="flex gap-2">
              <RadioGroupOption v-for="env in environments" :key="env" :value="env" v-slot="{ checked }">
                <div class="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer transition-all"
                  :class="checked ? 'bg-[var(--accent-color)] text-white shadow-lg' : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]/80'">
                  {{ env }}
                </div>
              </RadioGroupOption>
            </RadioGroup>
          </div>

          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-sm text-[var(--text-secondary)] mb-2">轴长 (s)</label>
              <input v-model="editTeam.axisLength" type="text" placeholder="示例：20"
                class="w-full px-3 py-2.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
            </div>
            <div>
              <label class="block text-sm text-[var(--text-secondary)] mb-2">DPS (w)</label>
              <div class="relative">
                <input v-model="editTeam.dps" @input="calculateDPS" type="text" placeholder="示例：0"
                  class="w-full px-3 py-2.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 pr-8">
                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[var(--text-tertiary)]">w</span>
              </div>
            </div>
            <div>
              <label class="block text-sm text-[var(--text-secondary)] mb-2">难度</label>
              <Listbox v-model="editTeam.difficulty">
                <div class="relative">
                  <ListboxButton class="w-full px-3 py-2.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] text-center cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
                    {{ editTeam.difficulty }}
                  </ListboxButton>
                  <ListboxOptions class="absolute z-10 mt-1 w-full bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-xl shadow-lg overflow-hidden">
                    <ListboxOption v-for="d in difficulties" :key="d" :value="d" v-slot="{ active, selected }">
                      <div class="px-3 py-2.5 text-sm text-center cursor-pointer transition-all" :class="active ? 'bg-[var(--accent-color)] text-white' : 'text-[var(--text-primary)]'">{{ d }}</div>
                    </ListboxOption>
                  </ListboxOptions>
                </div>
              </Listbox>
            </div>
          </div>

          <div>
            <label class="block text-sm text-[var(--text-secondary)] mb-2">贡献者</label>
            <input :value="authStore.user?.username" readonly type="text"
              class="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-secondary)] cursor-not-allowed">
          </div>
        </div>

        <div class="p-5 border-t border-[var(--border-color)] flex gap-3 bg-[var(--bg-tertiary)]/30">
          <button @click="close" class="flex-1 py-3 rounded-xl bg-[var(--bg-tertiary)] text-[var(--text-primary)] font-medium text-sm hover:opacity-80 transition-all">取消</button>
          <button @click="saveTeam" class="flex-1 py-3 rounded-xl bg-[var(--accent-color)] text-white font-medium text-sm hover:opacity-90 transition-all shadow-lg shadow-[var(--accent-color)]/20">保存</button>
        </div>
      </DialogPanel>
    </div>

    <Teleport to="body">
      <Dialog v-if="showAxisEditor" :open="showAxisEditor" @close="cancelAxisEdit" class="relative z-[100]">
        <div class="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60"></div>
          <DialogPanel class="relative w-full max-w-[1600px] bg-[var(--bg-secondary)] rounded-2xl shadow-2xl border border-[var(--border-color)] overflow-hidden max-h-[95vh] flex flex-col">
            <div class="flex items-center justify-between p-5 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]/30 flex-shrink-0">
              <div class="flex items-center gap-3">
                <DialogTitle class="text-lg font-semibold text-[var(--text-primary)]">{{ editingAxisIndex >= 0 ? '编辑轴' : '添加轴' }}</DialogTitle>
              </div>
              <div class="flex items-center gap-3">
                <div class="flex items-center gap-2 relative">
                  <label class="text-sm text-[var(--text-secondary)]">轴名称:</label>
                  <div class="relative">
                    <input v-model="axisForm.name" type="text" placeholder="输入轴名称" @focus="showAxisNameDropdown = true" @blur="handleAxisNameBlur"
                      class="px-3 py-1.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 w-40">
                    <div v-if="showAxisNameDropdown" class="absolute top-full left-0 mt-1 w-full bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg shadow-xl z-50 overflow-hidden">
                      <button v-for="name in quickAxisNames" :key="name" @mousedown.prevent="axisForm.name = name; showAxisNameDropdown = false"
                        class="w-full px-3 py-2 text-left text-sm text-[var(--text-primary)] hover:bg-[var(--accent-color)] hover:text-white transition-colors">{{ name }}</button>
                    </div>
                  </div>
                </div>
                <button @click="cancelAxisEdit" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)] transition-colors">
                  <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto min-h-0">
              <RotationEdit :characters="selectedCharNames" :total-duration="30" :initial-video-url="axisForm.videoUrl" :initial-segments="axisForm.rotationData?.segments" @save="saveAxis" @cancel="cancelAxisEdit" />
            </div>
          </DialogPanel>
        </div>
      </Dialog>
    </Teleport>

    <Dialog :open="showCharacterPicker" @close="showCharacterPicker = false" class="relative z-60">
      <div class="fixed inset-0 z-60 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/60"></div>
        <DialogPanel class="relative w-full max-w-3xl bg-[var(--bg-secondary)] rounded-2xl shadow-2xl border border-[var(--border-color)] overflow-hidden max-h-[80vh] flex flex-col">
          <div class="flex items-center justify-between p-4 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]/30">
            <DialogTitle class="text-lg font-semibold text-[var(--text-primary)]">选择角色</DialogTitle>
            <button @click="showCharacterPicker = false" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)]">
              <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-4">
            <div class="grid grid-cols-5 gap-3">
              <div v-for="char in allCharacters" :key="char.id" @click="selectCharacter(char)"
                class="rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--accent-color)]/20 border-2 border-transparent hover:border-[var(--accent-color)] cursor-pointer transition-all flex flex-col items-center justify-center p-3 overflow-hidden">
                <img :src="`/assets/characters/${char.name}.webp`" :alt="char.name" class="w-14 h-14 object-contain mb-1.5" @error="$event.target.style.display = 'none'">
                <span class="text-[10px] text-[var(--text-primary)] text-center truncate w-full">{{ char.name }}</span>
                <div class="flex items-center gap-1 mt-1">
                  <img :src="`/assets/icons/${char.element}.webp`" class="w-3.5 h-3.5 object-contain">
                  <img :src="`/assets/icons/${char.weapon}.webp`" class="w-3.5 h-3.5 object-contain">
                  <span :class="char.star === 5 ? 'text-amber-400' : 'text-purple-400'" class="text-[8px]">★</span>
                </div>
              </div>
            </div>
          </div>
        </DialogPanel>
      </div>
    </Dialog>

    <Dialog :open="showAlert" @close="showAlert = false" class="relative z-70">
      <div class="fixed inset-0 z-70 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/60"></div>
        <DialogPanel class="relative w-full max-w-sm bg-[var(--bg-secondary)] rounded-2xl shadow-2xl border border-[var(--border-color)] p-6">
          <DialogTitle class="text-base font-semibold text-[var(--text-primary)] text-center mb-4">{{ alertMessage }}</DialogTitle>
          <button @click="showAlert = false" class="w-full py-2.5 rounded-xl bg-[var(--accent-color)] text-white font-medium text-sm">确定</button>
        </DialogPanel>
      </div>
    </Dialog>
  </Dialog>
</template>
