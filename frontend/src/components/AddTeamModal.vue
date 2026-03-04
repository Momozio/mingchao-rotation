<script setup>
import { ref, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild, RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'

const emit = defineEmits(['save', 'close'])

const allCharacters = ref([])
const selectingIndex = ref(null)
const showCharacterPicker = ref(false)

const newTeam = ref({
  name: '',
  remark: '',
  axisLength: '',
  dps: '',
  matrixScore: '',
  difficulty: '中等',
  environment: '通用',
  flow: { startup: '', loop: '' },
  contributors: 'mozz',
  characters: [
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' },
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' },
    { id: null, name: null, star: null, weapon: null, element: null, energy: '' }
  ]
})

const environments = ['通用', '海虚满协奏']
const difficulties = ['简单', '中等', '困难']

const calculateDPS = (event) => {
  const value = event.target.value.replace(/[^\d.]/g, '')
  newTeam.value.dps = value
  if (value) {
    const num = parseFloat(value)
    if (!isNaN(num)) newTeam.value.matrixScore = Math.round(num * 1200 * 100) / 100
  }
}

const calculateMatrix = (event) => {
  const value = event.target.value.replace(/[^\d.]/g, '')
  newTeam.value.matrixScore = value
  if (value) {
    const num = parseFloat(value)
    if (!isNaN(num)) newTeam.value.dps = (num / 1200).toFixed(2)
  }
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
  newTeam.value.characters[selectingIndex.value] = {
    id: char.id, name: char.name, star: char.star, weapon: char.weapon, element: char.element, energy: ''
  }
  showCharacterPicker.value = false
  selectingIndex.value = null
}

const removeCharacter = (index) => {
  newTeam.value.characters[index] = { id: null, name: null, star: null, weapon: null, element: null, energy: '' }
}

const handleEnergyInput = (char, event) => {
  let value = event.target.value.replace(/[^\d%]/g, '')
  if (value && !value.endsWith('%')) value = value.replace('%', '') + '%'
  char.energy = value
}

const saveTeam = () => {
  if (!newTeam.value.name.trim()) return alert('请输入配队名称')
  const selectedChars = newTeam.value.characters.filter(c => c.id !== null)
  if (selectedChars.length === 0) return alert('请至少选择1名角色')
  emit('save', { ...newTeam.value, characters: selectedChars })
}

onMounted(() => fetchCharacters())
</script>

<template>
  <TransitionRoot appear :show="true" as="template">
    <Dialog as="div" @close="emit('close')" class="relative z-50">
      <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0" enter-to="opacity-100" leave="duration-200 ease-in" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-black/70" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0 scale-95" enter-to="opacity-100 scale-100" leave="duration-200 ease-in" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
            <DialogPanel class="w-full max-w-2xl bg-[var(--bg-secondary)] rounded-2xl shadow-2xl border border-[var(--border-color)] overflow-hidden">
              <div class="flex items-center justify-between p-5 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]/30">
                <DialogTitle class="text-lg font-semibold text-[var(--text-primary)]">添加配队</DialogTitle>
                <button @click="emit('close')" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)] transition-colors">
                  <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>

              <div class="p-5 space-y-5 max-h-[70vh] overflow-y-auto">
                <div>
                  <label class="block text-sm text-[var(--text-secondary)] mb-2">配队名称 <span class="text-red-400">*</span></label>
                  <input v-model="newTeam.name" type="text" placeholder="输入配队名称" class="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
                </div>

                <div>
                  <label class="block text-sm text-[var(--text-secondary)] mb-2">备注</label>
                  <input v-model="newTeam.remark" type="text" placeholder="补充说明" class="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
                </div>

                <div>
                  <label class="block text-sm text-[var(--text-secondary)] mb-2">选择角色 <span class="text-red-400">*</span></label>
                  <div class="flex justify-center gap-4 mb-3">
                    <div v-for="(char, index) in newTeam.characters" :key="index" class="w-28">
                      <div v-if="char.id" class="relative group">
                        <div class="aspect-square rounded-2xl bg-[var(--bg-tertiary)] border-2 border-[var(--accent-color)] flex flex-col items-center justify-center p-2 overflow-hidden">
                          <img :src="`/assets/characters/${char.name}.webp`" :alt="char.name" class="w-16 h-16 object-contain" @error="$event.target.style.display='none'">
                          <span class="text-[10px] text-[var(--text-primary)] truncate w-full text-center">{{ char.name }}</span>
                        </div>
                        <button @click="removeCharacter(index)" class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                        </button>
                        <input v-model="char.energy" @input="handleEnergyInput(char, $event)" type="text" placeholder="默认无需求" class="w-full mt-2 px-2 py-1.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-lg text-xs text-[var(--text-primary)] text-center">
                        <div class="text-[10px] text-cyan-400 text-center mt-0.5">充能需求</div>
                      </div>
                      <div v-else @click="openCharacterPicker(index)" class="aspect-square rounded-2xl border-2 border-dashed border-[var(--border-color)] flex items-center justify-center cursor-pointer hover:border-[var(--accent-color)] hover:bg-[var(--bg-tertiary)] transition-all bg-[var(--bg-tertiary)]/50">
                        <span class="text-sm text-[var(--text-tertiary)]">+ 选择</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <label class="block text-sm text-[var(--text-secondary)] mb-2">适配环境</label>
                  <RadioGroup v-model="newTeam.environment" class="flex gap-2">
                    <RadioGroupOption v-for="env in environments" :key="env" v-slot="{ checked }">
                      <div class="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer transition-all" :class="checked ? 'bg-[var(--accent-color)] text-white shadow-lg' : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]/80'">
                        {{ env }}
                      </div>
                    </RadioGroupOption>
                  </RadioGroup>
                </div>

                <div class="grid grid-cols-3 gap-3">
                  <div>
                    <label class="block text-sm text-[var(--text-secondary)] mb-2">轴长(s)</label>
                    <input v-model="newTeam.axisLength" type="text" placeholder="20" class="w-full px-3 py-2.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
                  </div>
                  <div>
                    <label class="block text-sm text-[var(--text-secondary)] mb-2">DPS / 矩阵</label>
                    <div class="space-y-2">
                      <input v-model="newTeam.dps" @input="calculateDPS" type="text" placeholder="DPS" class="w-full px-2 py-2 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-lg text-xs text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
                      <input v-model="newTeam.matrixScore" @input="calculateMatrix" type="text" placeholder="矩阵" class="w-full px-2 py-2 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-lg text-xs text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm text-[var(--text-secondary)] mb-2">难度</label>
                    <div class="relative">
                      <select v-model="newTeam.difficulty" class="w-full px-3 py-2.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] text-center focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 cursor-pointer appearance-none">
                        <option v-for="d in difficulties" :key="d" :value="d">{{ d }}</option>
                      </select>
                      <svg class="w-4 h-4 text-[var(--text-tertiary)] absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                    </div>
                  </div>
                </div>

                <div>
                  <label class="block text-sm text-[var(--text-secondary)] mb-2">启动轴</label>
                  <textarea v-model="newTeam.flow.startup" placeholder="角色A开E→角色B QTE→角色C E..." rows="2" class="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 resize-none"></textarea>
                </div>

                <div>
                  <label class="block text-sm text-[var(--text-secondary)] mb-2">循环轴</label>
                  <textarea v-model="newTeam.flow.loop" placeholder="角色A AAZ→角色B QTE→..." rows="2" class="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30 resize-none"></textarea>
                </div>

                <div>
                  <label class="block text-sm text-[var(--text-secondary)] mb-2">贡献者</label>
                  <input v-model="newTeam.contributors" type="text" placeholder="贡献者" class="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]/30">
                </div>
              </div>

              <div class="p-5 border-t border-[var(--border-color)] flex gap-3 bg-[var(--bg-tertiary)]/30">
                <button @click="emit('close')" class="flex-1 py-3 rounded-xl bg-[var(--bg-tertiary)] text-[var(--text-primary)] font-medium text-sm hover:opacity-80 transition-all">取消</button>
                <button @click="saveTeam" class="flex-1 py-3 rounded-xl bg-[var(--accent-color)] text-white font-medium text-sm hover:opacity-90 transition-all shadow-lg shadow-[var(--accent-color)]/20">保存</button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>

    <TransitionRoot appear :show="showCharacterPicker" as="template">
      <Dialog as="div" @close="showCharacterPicker = false" class="relative z-60">
        <TransitionChild as="template" enter="duration-200 ease-out" enter-from="opacity-0" enter-to="opacity-100" leave="duration-150 ease-in" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-black/70" />
        </TransitionChild>
        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4">
            <TransitionChild as="template" enter="duration-200 ease-out" enter-from="opacity-0 scale-95" enter-to="opacity-100 scale-100" leave="duration-150 ease-in" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
              <DialogPanel class="w-full max-w-3xl bg-[var(--bg-secondary)] rounded-2xl shadow-2xl border border-[var(--border-color)] overflow-hidden max-h-[80vh] flex flex-col">
                <div class="flex items-center justify-between p-4 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]/30">
                  <DialogTitle class="text-lg font-semibold text-[var(--text-primary)]">选择角色</DialogTitle>
                  <button @click="showCharacterPicker = false" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)]">
                    <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </div>
                <div class="flex-1 overflow-y-auto p-4">
                  <div class="grid grid-cols-5 gap-3">
                    <div v-for="char in allCharacters" :key="char.id" @click="selectCharacter(char)" class="rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--accent-color)]/20 border-2 border-transparent hover:border-[var(--accent-color)] cursor-pointer transition-all flex flex-col items-center justify-center p-3 overflow-hidden">
                      <img :src="`/assets/characters/${char.name}.webp`" :alt="char.name" class="w-14 h-14 object-contain mb-1.5" @error="$event.target.style.display='none'">
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
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </TransitionRoot>
</template>