<script setup lang="ts">
import { ref, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import RotationPlayer from './RotationPlayer.vue'

interface Character {
  character_id: number
  character_name: string
  energy: string
  order: number
  element?: string
  weapon?: string
}

interface Axis {
  id: number
  name: string
  video_url?: string
  total_duration: number
  segments_data: { [key: string]: any[] }
  characters: { name: string; segments: any[] }[]
  order: number
}

interface Team {
  id: number
  name: string
  remark?: string
  team_characters: Character[]
  axes: Axis[]
}

const props = defineProps<{
  modelValue: boolean
  team: Team | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const axisCurrentTimes = ref<{ [key: number]: number }>({})
const isPlaying = ref<{ [key: number]: boolean }>({})
const videoRefs = ref<HTMLVideoElement[]>([])
const animationFrames = ref<{ [key: number]: number }>({})
const axisDurations = ref<{ [key: number]: number }>({})

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

watch(() => props.team, (newTeam) => {
  if (newTeam && newTeam.axes) {
    newTeam.axes.forEach((axis, index) => {
      axisDurations.value[index] = axis.total_duration || 30
    })
  }
}, { immediate: true })

const close = () => {
  emit('update:modelValue', false)
  stopAllPlayback()
}

// 停止所有播放
const stopAllPlayback = () => {
  Object.values(animationFrames.value).forEach(frame => {
    if (frame) cancelAnimationFrame(frame)
  })
  animationFrames.value = {}
  
  videoRefs.value.forEach(video => {
    if (video) {
      video.pause()
      video.currentTime = 0
    }
  })
  
  Object.keys(isPlaying.value).forEach(key => {
    isPlaying.value[key] = false
  })
  Object.keys(axisCurrentTimes.value).forEach(key => {
    axisCurrentTimes.value[key] = 0
  })
}

// 启动无视频时的播放动画
const startPlaybackAnimation = (axisIndex: number, totalDuration: number) => {
  const startTime = Date.now() - (axisCurrentTimes.value[axisIndex] || 0) * 1000
  
  const animate = () => {
    if (!isPlaying.value[axisIndex]) return
    
    const elapsed = (Date.now() - startTime) / 1000
    if (elapsed >= totalDuration) {
      axisCurrentTimes.value[axisIndex] = totalDuration
      isPlaying.value[axisIndex] = false
      animationFrames.value[axisIndex] = null
      return
    }
    
    axisCurrentTimes.value[axisIndex] = elapsed
    animationFrames.value[axisIndex] = requestAnimationFrame(animate)
  }
  
  animationFrames.value[axisIndex] = requestAnimationFrame(animate)
}

// 切换播放/暂停
const togglePlay = (axisIndex: number) => {
  const video = videoRefs.value[axisIndex]
  
  if (video) {
    if (isPlaying.value[axisIndex]) {
      video.pause()
      isPlaying.value[axisIndex] = false
    } else {
      video.play()
      isPlaying.value[axisIndex] = true
    }
  } else {
    if (isPlaying.value[axisIndex]) {
      isPlaying.value[axisIndex] = false
      if (animationFrames.value[axisIndex]) {
        cancelAnimationFrame(animationFrames.value[axisIndex])
        animationFrames.value[axisIndex] = null
      }
    } else {
      isPlaying.value[axisIndex] = true
      const totalDuration = axisDurations.value[axisIndex] || 30
      startPlaybackAnimation(axisIndex, totalDuration)
    }
  }
}

// 重置播放
const resetPlayback = (axisIndex: number) => {
  const video = videoRefs.value[axisIndex]
  if (video) {
    video.pause()
    video.currentTime = 0
  }
  
  if (animationFrames.value[axisIndex]) {
    cancelAnimationFrame(animationFrames.value[axisIndex])
    animationFrames.value[axisIndex] = null
  }
  
  isPlaying.value[axisIndex] = false
  axisCurrentTimes.value[axisIndex] = 0
}

// 视频播放事件
const handleVideoPlay = (axisIndex: number) => {
  isPlaying.value[axisIndex] = true
}

// 视频暂停事件
const handleVideoPause = (axisIndex: number) => {
  isPlaying.value[axisIndex] = false
}

// 视频时间更新
const handleVideoTimeUpdate = (event: Event, axisIndex: number) => {
  const video = event.target as HTMLVideoElement
  axisCurrentTimes.value[axisIndex] = video.currentTime
}

// 时间轴 seek
const handleAxisSeek = (axisIndex: number, time: number) => {
  axisCurrentTimes.value[axisIndex] = time
  
  const video = videoRefs.value[axisIndex]
  if (video) {
    video.currentTime = time
  }
}

// 格式化时间
const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 获取 RotationPlayer 数据
const getAxisRotation = (axis: Axis) => {
  if (!axis || !axis.characters) return null
  
  return {
    name: axis.name,
    totalDuration: axis.total_duration || 30,
    characters: axis.characters.map(char => ({
      name: char.name,
      segments: char.segments || []
    }))
  }
}
</script>

<template>
  <Teleport to="body">
    <Dialog 
      v-if="modelValue" 
      :open="modelValue" 
      @close="close" 
      class="relative z-[100]">
      <div class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm"></div>
        <DialogPanel
          class="relative w-full max-w-5xl bg-[var(--bg-secondary)] rounded-2xl shadow-2xl border border-[var(--border-color)] overflow-hidden max-h-[90vh] flex flex-col">
          
          <!-- 弹窗头部 -->
          <div class="flex items-center justify-between p-5 border-b border-[var(--border-color)] bg-[var(--bg-tertiary)]/50 flex-shrink-0">
            <div>
              <DialogTitle class="text-xl font-semibold text-[var(--text-primary)]">
                {{ team?.name }}
              </DialogTitle>
              <p v-if="team?.remark" class="text-xs text-[var(--text-secondary)] mt-1">{{ team.remark }}</p>
            </div>
            <button @click="close" class="p-2 rounded-xl hover:bg-[var(--bg-tertiary)] transition-colors">
              <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- 弹窗内容 -->
          <div class="flex-1 overflow-y-auto p-5 space-y-5">
            <!-- 角色展示 -->
            <div>
              <div class="text-sm font-medium text-[var(--text-secondary)] mb-3">配队角色</div>
              <div class="grid grid-cols-3 gap-3">
                <div 
                  v-for="(char, idx) in team?.team_characters" 
                  :key="idx"
                  class="bg-gradient-to-br from-[var(--bg-tertiary)] to-[var(--bg-secondary)] rounded-xl p-3 border border-[var(--border-color)]/50">
                  <div class="flex gap-3">
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
                    <div class="flex-1 min-w-0 flex flex-col justify-center py-0.5">
                      <div class="text-sm font-semibold text-[var(--text-primary)] truncate leading-tight mb-1.5">
                        {{ char.character_name }}
                      </div>
                      <div class="flex items-center gap-1.5">
                        <div :class="['flex items-center gap-1 rounded-md px-2 py-1 border', getElementColor(getCharacterInfo(char.character_name).element).bg, getElementColor(getCharacterInfo(char.character_name).element).border]">
                          <img :src="`/assets/icons/${getCharacterInfo(char.character_name).element}.webp`" 
                               class="w-3.5 h-3.5 object-contain"
                               :style="{ filter: getElementColor(getCharacterInfo(char.character_name).element).filter }">
                          <span :class="['text-[9px] font-medium', getElementColor(getCharacterInfo(char.character_name).element).text]">{{ getCharacterInfo(char.character_name).element }}</span>
                        </div>
                        <div class="flex items-center gap-1 bg-[var(--bg-secondary)] rounded-md px-2 py-1 border border-[var(--border-color)]/30">
                          <img :src="`/assets/icons/${getCharacterInfo(char.character_name).weapon}.webp`" 
                               class="w-3.5 h-3.5 object-contain">
                          <span class="text-[9px] text-[var(--text-secondary)]">{{ getCharacterInfo(char.character_name).weapon }}</span>
                        </div>
                      </div>
                      <div class="mt-2">
                        <span v-if="char.energy" class="text-[10px] font-medium text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-md border border-blue-500/20">
                          ⚡ {{ char.energy }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 轴详情 -->
            <div v-if="team?.axes && team.axes.length > 0">
              <div class="text-sm font-medium text-[var(--text-secondary)] mb-3">输出轴详情</div>
              <div class="space-y-4">
                <div 
                  v-for="(axis, axisIndex) in team.axes" 
                  :key="axis.id || axisIndex"
                  class="bg-[var(--bg-tertiary)] rounded-xl border border-[var(--border-color)] overflow-hidden">
                  
                  <!-- 轴标题 -->
                  <div class="px-4 py-3 border-b border-[var(--border-color)] flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <span class="text-base font-semibold text-[var(--text-primary)]">{{ axis.name }}</span>
                      <span class="text-xs text-[var(--text-tertiary)] bg-[var(--bg-secondary)] px-2 py-0.5 rounded">{{ axis.total_duration }}s</span>
                    </div>
                  </div>
                  
                  <div class="p-4">
                    <!-- 视频区域（上部） -->
                    <div v-if="axis.video_url" class="bg-black rounded-xl overflow-hidden mb-4">
                      <video 
                        ref="videoRefs"
                        :src="`/media/videos/${axis.video_url}`"
                        class="w-full h-full max-h-[350px]"
                        @play="handleVideoPlay(axisIndex)"
                        @pause="handleVideoPause(axisIndex)"
                        @timeupdate="handleVideoTimeUpdate($event, axisIndex)"
                      ></video>
                    </div>
                    <div v-else class="bg-[var(--bg-secondary)] rounded-xl flex items-center justify-center text-[var(--text-tertiary)] text-sm border-2 border-dashed border-[var(--border-color)] py-12 mb-4">
                      <div class="text-center">
                        <svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        <span>暂无视频</span>
                      </div>
                    </div>
                    
                    <!-- 时间轴区域（下部） -->
                    <div class="bg-[var(--bg-tertiary)] rounded-xl border border-[var(--border-color)] overflow-hidden">
                      <!-- 播放控制栏（中间） -->
                      <div class="px-4 py-3 border-b border-[var(--border-color)] flex items-center justify-between bg-[var(--bg-secondary)]">
                        <div class="flex items-center gap-3">
                          <!-- 播放控制按钮 -->
                          <div class="flex items-center gap-1">
                            <button 
                              @click="togglePlay(axisIndex)"
                              class="p-2 rounded-lg hover:bg-[var(--bg-tertiary)] transition-colors"
                              :title="isPlaying[axisIndex] ? '暂停' : '播放'">
                              <svg v-if="isPlaying[axisIndex]" class="w-5 h-5 text-[var(--text-primary)]" fill="currentColor" viewBox="0 0 24 24">
                                <rect x="6" y="4" width="4" height="16" rx="1"></rect>
                                <rect x="14" y="4" width="4" height="16" rx="1"></rect>
                              </svg>
                              <svg v-else class="w-5 h-5 text-[var(--text-primary)]" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M8 5v14l11-7z"></path>
                              </svg>
                            </button>
                            <button 
                              @click="resetPlayback(axisIndex)"
                              class="p-2 rounded-lg hover:bg-[var(--bg-tertiary)] transition-colors"
                              title="重置">
                              <svg class="w-5 h-5 text-[var(--text-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                            </button>
                          </div>
                          <!-- 分隔线 -->
                          <div class="w-px h-6 bg-[var(--border-color)]"></div>
                          <!-- 时间显示 -->
                          <div class="text-sm font-medium text-[var(--text-primary)]">
                            {{ formatTime(axisCurrentTimes[axisIndex] || 0) }}
                            <span class="text-[var(--text-tertiary)]"> / {{ formatTime(axis.total_duration) }}</span>
                          </div>
                        </div>
                        <!-- 右侧视频标识 -->
                        <span v-if="axis.video_url" class="text-xs text-[var(--accent-color)] flex items-center gap-1 bg-[var(--accent-color)]/10 px-2 py-1 rounded">
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          同步播放中
                        </span>
                      </div>
                      <!-- RotationPlayer -->
                      <div class="p-3">
                        <RotationPlayer
                          v-if="getAxisRotation(axis)"
                          :rotation="getAxisRotation(axis)"
                          :current-time="axisCurrentTimes[axisIndex] || 0"
                          @seek="(time) => handleAxisSeek(axisIndex, time)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-12 text-[var(--text-tertiary)]">
              <div class="text-sm">暂无输出轴数据</div>
            </div>
          </div>
        </DialogPanel>
      </div>
    </Dialog>
  </Teleport>
</template>
