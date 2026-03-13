<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

interface Character {
  character_id: number
  character_name: string
  energy: string
  order: number
  element?: string
  weapon?: string
  star?: number
}

interface Team {
  id: number
  name: string
  remark?: string
  axis_length?: number
  dps?: number
  matrix_score?: number
  difficulty: string
  environment: string
  contributors: string
  team_characters: Character[]
  created_by?: {
    id: number
    username: string
  }
  created_at: string
  updated_at: string
}

const props = defineProps<{
  team: Team
  isGridView?: boolean
}>()

const isGridView = computed(() => props.isGridView ?? false)

const emit = defineEmits<{
  view: [team: Team]
  delete: [id: number, createdBy: number]
}>()

const canDelete = computed(() => {
  if (!authStore.isAuthenticated) return false
  if (!props.team.created_by) return false
  return authStore.user?.id === props.team.created_by.id
})

// 元素颜色映射
const elementColors: Record<string, { text: string; bg: string; border: string; filter: string }> = {
  '冷凝': { text: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20', filter: 'brightness(0) saturate(100%) invert(1) sepia(1) saturate(3) hue-rotate(160deg)' },
  '导电': { text: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20', filter: 'brightness(0) saturate(100%) invert(1) sepia(1) saturate(3) hue-rotate(240deg)' },
  '气动': { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', filter: 'brightness(0) saturate(100%) invert(1) sepia(1) saturate(3) hue-rotate(120deg)' },
  '湮灭': { text: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20', filter: 'brightness(0) saturate(100%) invert(1) sepia(1) saturate(3) hue-rotate(300deg)' },
  '热熔': { text: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20', filter: 'brightness(0) saturate(100%) invert(1) sepia(1) saturate(3) hue-rotate(10deg)' },
  '衍射': { text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', filter: 'brightness(0) saturate(100%) invert(1) sepia(1) saturate(3) hue-rotate(35deg)' }
}

const getElementColor = (element?: string) => {
  return elementColors[element || '冷凝'] || elementColors['冷凝']
}

// 角色元素和武器映射
const characterData: Record<string, { element: string; weapon: string }> = {
  '漂泊者·衍射': { element: '衍射', weapon: '迅刀' },
  '漂泊者·湮灭': { element: '湮灭', weapon: '迅刀' },
  '漂泊者·气动': { element: '气动', weapon: '迅刀' },
  '安可': { element: '热熔', weapon: '音感仪' },
  '维里奈': { element: '衍射', weapon: '音感仪' },
  '凌阳': { element: '冷凝', weapon: '臂铠' },
  '鉴心': { element: '气动', weapon: '臂铠' },
  '卡卡罗': { element: '导电', weapon: '长刃' },
  '忌炎': { element: '气动', weapon: '长刃' },
  '今汐': { element: '衍射', weapon: '长刃' },
  '长离': { element: '热熔', weapon: '迅刀' },
  '椿': { element: '湮灭', weapon: '迅刀' },
  '相里要': { element: '导电', weapon: '臂铠' },
  '守岸人': { element: '衍射', weapon: '音感仪' },
  '卡提希娅': { element: '气动', weapon: '迅刀' },
  '坎特蕾拉': { element: '湮灭', weapon: '音感仪' },
  '珂莱塔': { element: '冷凝', weapon: '佩枪' },
  '弗洛洛': { element: '湮灭', weapon: '音感仪' },
  '琳奈': { element: '衍射', weapon: '佩枪' },
  '莫宁': { element: '热熔', weapon: '长刃' },
  '爱弥斯': { element: '热熔', weapon: '迅刀' },
  '陆·赫斯': { element: '衍射', weapon: '臂铠' },
  '仇远': { element: '气动', weapon: '迅刀' },
  '嘉贝莉娜': { element: '热熔', weapon: '佩枪' },
  '露帕': { element: '热熔', weapon: '长刃' },
  '折枝': { element: '冷凝', weapon: '音感仪' },
  '千咲': { element: '湮灭', weapon: '长刃' },
  '卜灵': { element: '导电', weapon: '音感仪' },
  '吟霖': { element: '导电', weapon: '音感仪' },
  '夏空': { element: '气动', weapon: '佩枪' },
  '奥古斯塔': { element: '导电', weapon: '长刃' },
  '尤诺': { element: '气动', weapon: '臂铠' },
  '布兰特': { element: '热熔', weapon: '迅刀' },
  '洛可可': { element: '湮灭', weapon: '臂铠' },
  '菲比': { element: '衍射', weapon: '音感仪' },
  '赞妮': { element: '衍射', weapon: '臂铠' },
  '秧秧': { element: '气动', weapon: '迅刀' },
  '白芷': { element: '冷凝', weapon: '音感仪' },
  '炽霞': { element: '热熔', weapon: '佩枪' },
  '散华': { element: '冷凝', weapon: '迅刀' },
  '秋水': { element: '气动', weapon: '佩枪' },
  '丹瑾': { element: '湮灭', weapon: '迅刀' },
  '莫特斐': { element: '热熔', weapon: '佩枪' },
  '渊武': { element: '导电', weapon: '臂铠' },
  '桃祈': { element: '湮灭', weapon: '长刃' },
  '灯灯': { element: '导电', weapon: '长刃' },
  '釉瑚': { element: '冷凝', weapon: '臂铠' }
}

const getCharacterInfo = (charName?: string) => {
  if (!charName) return { element: '冷凝', weapon: '迅刀' }
  return characterData[charName] || { element: '冷凝', weapon: '迅刀' }
}

// 相对时间格式化
const formatRelativeTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)}天前`
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const handleView = () => {
  emit('view', props.team)
}

const handleDelete = (event: Event) => {
  event.stopPropagation()
  emit('delete', props.team.id, props.team.created_by?.id)
}
</script>

<template>
  <div 
    class="bg-[var(--bg-secondary)] rounded-2xl shadow-lg border border-[var(--border-color)] overflow-hidden transition-all duration-300 group hover:border-[var(--accent-color)]/30">
    
    <!-- 卡片头部 -->
    <div class="relative p-5 pb-4">
      <div class="flex items-start justify-between pr-20">
        <div>
          <h3 class="text-lg font-semibold text-[var(--text-primary)]">{{ team.name }}</h3>
          <p v-if="team.remark" class="text-xs text-[var(--text-secondary)] mt-1.5 line-clamp-1">{{ team.remark }}</p>
        </div>
      </div>
      
      <!-- 查看按钮 -->
      <button 
        @click.stop="handleView"
        class="absolute top-4 right-4 px-3 py-1.5 rounded-lg bg-[var(--accent-color)]/15 text-[var(--accent-color)] text-xs font-medium 
               hover:bg-[var(--accent-color)] hover:text-white transition-all duration-200">
        查看
      </button>
      
      <!-- 删除按钮 - 右上角悬停显示 (在查看按钮左边) -->
      <button 
        v-if="canDelete"
        @click.stop="handleDelete"
        class="absolute top-4 right-[5.5rem] p-2 rounded-xl opacity-0 group-hover:opacity-100 
               hover:bg-red-500/15 transition-all duration-200 group/delete">
        <svg class="w-4 h-4 text-red-400 group-hover/delete:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- 角色区域 - 三列布局 -->
    <div class="px-5 pb-4">
      <div :class="isGridView ? 'flex flex-col gap-3' : 'grid grid-cols-3 gap-3'">
        <div 
          v-for="(char, idx) in team.team_characters" 
          :key="idx"
          class="bg-gradient-to-br from-[var(--bg-tertiary)] to-[var(--bg-secondary)] rounded-xl p-3 border border-[var(--border-color)]/50">
          <div :class="['flex', isGridView ? 'flex-row gap-3' : 'gap-3']">
            <!-- 头像区域 -->
            <div :class="['relative flex-shrink-0', isGridView ? 'mx-auto' : '']">
              <div :class="['rounded-xl bg-[var(--bg-secondary)] flex items-center justify-center overflow-hidden border border-[var(--border-color)]/30', isGridView ? 'w-14 h-14 p-1.5' : 'w-16 h-16 p-1.5']">
                <img 
                  :src="`/assets/characters/${char.character_name}.webp`" 
                  :alt="char.character_name"
                  class="w-full h-full object-contain filter drop-shadow-xl"
                  @error="$event.target.style.display='none'"
                >
              </div>
            </div>
            
            <!-- 信息区域 -->
            <div :class="['flex-1 min-w-0', isGridView ? 'flex flex-col items-center text-center' : 'flex flex-col justify-center py-0.5']">
              <!-- 角色名 -->
              <div :class="['font-semibold text-[var(--text-primary)] truncate leading-tight mb-1.5', isGridView ? 'text-sm' : 'text-sm']">
                {{ char.character_name }}
              </div>
              <!-- 元素和武器 -->
              <div :class="['flex items-center gap-1.5', isGridView ? 'justify-center' : '']">
                <div :class="['flex items-center gap-1 rounded-md px-2 py-1 border', getElementColor(getCharacterInfo(char.character_name).element).bg, getElementColor(getCharacterInfo(char.character_name).element).border]">
                  <img :src="`/assets/icons/${getCharacterInfo(char.character_name).element}.webp`" 
                       class="w-3.5 h-3.5 object-contain" 
                       :style="{ filter: getElementColor(getCharacterInfo(char.character_name).element).filter }"
                       title="元素：{{ getCharacterInfo(char.character_name).element }}">
                  <span :class="['text-[9px] font-medium', getElementColor(getCharacterInfo(char.character_name).element).text]">{{ getCharacterInfo(char.character_name).element }}</span>
                </div>
                <div class="flex items-center gap-1 bg-[var(--bg-secondary)] rounded-md px-2 py-1 border border-[var(--border-color)]/30">
                  <img :src="`/assets/icons/${getCharacterInfo(char.character_name).weapon}.webp`" 
                       class="w-3.5 h-3.5 object-contain" 
                       title="武器：{{ getCharacterInfo(char.character_name).weapon }}">
                  <span class="text-[9px] text-[var(--text-secondary)]">{{ getCharacterInfo(char.character_name).weapon }}</span>
                </div>
              </div>
              <!-- 充能需求 -->
              <div class="mt-2">
                <span v-if="char.energy" class="text-[10px] font-medium text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-md border border-blue-500/20">
                  ⚡ {{ char.energy }}
                </span>
                <span v-else class="text-[16px] text-[var(--text-tertiary)] opacity-25 select-none">—</span>
              </div>
            </div>
          </div>
        </div>
        <!-- 占位卡片 - 不足 3 个角色时显示 -->
        <div 
          v-for="i in (3 - team.team_characters.length)" 
          :key="'empty-' + i"
          class="bg-[var(--bg-tertiary)]/30 rounded-xl p-3 flex items-center justify-center border-2 border-dashed border-[var(--border-color)]/50">
          <div class="text-center">
            <div class="w-16 h-16 rounded-xl bg-[var(--bg-secondary)] flex items-center justify-center mx-auto mb-2 border border-[var(--border-color)]/30">
              <svg class="w-7 h-7 text-[var(--text-tertiary)] opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div class="text-[10px] text-[var(--text-tertiary)]">空位</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 信息和数据 - 单行布局 -->
    <div class="px-5 pb-4">
      <!-- 环境、难度、轴长、DPS - 全部放在一行 -->
      <div class="grid grid-cols-4 gap-2">
        <div class="bg-[var(--bg-tertiary)] rounded-xl px-3 py-2 flex items-center justify-between">
          <span class="text-[9px] text-[var(--text-tertiary)]">环境</span>
          <span 
            v-if="team.environment"
            class="px-2 py-0.5 rounded text-[10px] font-medium"
            :class="{
              'bg-green-500/20 text-green-400': team.environment === '通用',
              'bg-blue-500/20 text-blue-400': team.environment.includes('海虚')
            }">
            {{ team.environment }}
          </span>
          <span v-else class="text-[10px] text-[var(--text-tertiary)]">-</span>
        </div>
        <div class="bg-[var(--bg-tertiary)] rounded-xl px-3 py-2 flex items-center justify-between">
          <span class="text-[9px] text-[var(--text-tertiary)]">难度</span>
          <span
            v-if="team.difficulty"
            class="px-2 py-0.5 rounded text-[10px] font-medium"
            :class="{
              'bg-green-500/20 text-green-400': team.difficulty === '简单',
              'bg-orange-500/20 text-orange-400': team.difficulty === '中等',
              'bg-red-500/20 text-red-400': team.difficulty === '困难'
            }">
            {{ team.difficulty }}
          </span>
          <span v-else class="text-[10px] text-[var(--text-tertiary)]">-</span>
        </div>
        <div class="bg-[var(--bg-tertiary)] rounded-xl px-3 py-2 flex items-center justify-between">
          <span class="text-[9px] text-[var(--text-tertiary)]">轴长</span>
          <span class="text-sm font-semibold text-[var(--text-primary)]">
            {{ team.axis_length || '-' }}
            <span class="text-[9px] text-[var(--text-tertiary)] ml-0.5">s</span>
          </span>
        </div>
        <div class="bg-[var(--bg-tertiary)] rounded-xl px-3 py-2 flex items-center justify-between">
          <span class="text-[9px] text-[var(--text-tertiary)]">DPS</span>
          <span class="text-sm font-semibold text-[var(--text-primary)]">
            {{ team.dps ? (team.dps / 10000).toFixed(0) : '-' }}
            <span class="text-[9px] text-[var(--text-tertiary)] ml-0.5">w</span>
          </span>
        </div>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="px-5 py-3 bg-[var(--bg-tertiary)]/30 border-t border-[var(--border-color)]/50 
                flex items-center justify-between text-xs text-[var(--text-tertiary)]">
      <span>贡献者：<span class="text-[var(--text-secondary)]">{{ team.contributors }}</span></span>
      <span>{{ formatRelativeTime(team.created_at) }}</span>
    </div>
  </div>
</template>
