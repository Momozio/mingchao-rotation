<script setup lang="ts">
import { ref } from 'vue'

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
  created_at: string
  updated_at: string
}

const props = defineProps<{
  team: Team
}>()

const emit = defineEmits<{
  view: [team: Team]
  delete: [id: number]
}>()

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
  emit('delete', props.team.id)
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
      <div class="grid grid-cols-3 gap-3">
        <div 
          v-for="(char, idx) in team.team_characters" 
          :key="idx"
          class="bg-gradient-to-br from-[var(--bg-tertiary)] to-[var(--bg-secondary)] rounded-xl p-3 border border-[var(--border-color)]/50">
          <div class="flex gap-3">
            <!-- 左侧头像 -->
            <div class="relative flex-shrink-0">
              <div class="w-16 h-16 rounded-xl bg-[var(--bg-secondary)] flex items-center justify-center p-1.5 overflow-hidden border border-[var(--border-color)]/30">
                <img 
                  :src="`/assets/characters/${char.character_name}.webp`" 
                  :alt="char.character_name"
                  class="w-full h-full object-contain filter drop-shadow-xl"
                  @error="$event.target.style.display='none'"
                >
              </div>
            </div>
            
            <!-- 右侧信息 -->
            <div class="flex-1 min-w-0 flex flex-col justify-center py-0.5">
              <!-- 角色名 -->
              <div class="text-sm font-semibold text-[var(--text-primary)] truncate leading-tight mb-1.5">
                {{ char.character_name }}
              </div>
              <!-- 元素和武器 -->
              <div class="flex items-center gap-1.5">
                <div class="flex items-center gap-1 bg-[var(--bg-secondary)] rounded-md px-2 py-1 border border-[var(--border-color)]/30">
                  <img :src="`/assets/icons/${char.element || '冷凝'}.webp`" 
                       class="w-3.5 h-3.5 object-contain" 
                       title="元素：{{ char.element || '冷凝' }}">
                  <span class="text-[9px] text-[var(--text-secondary)]">{{ char.element || '冷凝' }}</span>
                </div>
                <div class="flex items-center gap-1 bg-[var(--bg-secondary)] rounded-md px-2 py-1 border border-[var(--border-color)]/30">
                  <img :src="`/assets/icons/${char.weapon || '迅刀'}.webp`" 
                       class="w-3.5 h-3.5 object-contain" 
                       title="武器：{{ char.weapon || '迅刀' }}">
                  <span class="text-[9px] text-[var(--text-secondary)]">{{ char.weapon || '迅刀' }}</span>
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
