<template>
  <div class="test-action">
    <button @click="showDialog = true" class="open-btn">🎮 查看输出轴</button>

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showDialog" class="overlay" @click.self="showDialog = false">
          <div class="dialog">
            <div class="header">
              <h3>{{ currentRotation.name }}</h3>
              <button @click="showDialog = false" class="close-btn">✕</button>
            </div>

            <div class="controls">
              <button @click="togglePlay" class="play-btn">
                {{ isPlaying ? '⏸ 暂停' : '▶ 播放' }}
              </button>
              <button @click="reset" class="reset-btn">↺ 重置</button>
              <span class="time-display">{{ currentTime.toFixed(2) }}秒 / {{ currentRotation.totalDuration.toFixed(1) }}秒</span>
            </div>

            <RotationPlayer
              :rotation="currentRotation"
              :current-time="currentTime"
              @seek="handleSeek"
              ref="playerRef"
            />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import RotationPlayer from './RotationPlayer.vue'

interface Segment {
  type: 'action' | 'switch'
  startTime?: number
  endTime?: number
  time?: number
  display: string
  description?: string
  target?: string
}

interface CharacterData {
  name: string
  segments: Segment[]
}

interface Rotation {
  name: string
  totalDuration: number
  characters: CharacterData[]
}

const 启动轴: Rotation = {
  name: '漂泊者·湮灭 + 散华 + 维里奈 - 启动轴 (28s)',
  totalDuration: 28,
  characters: [
    {
      name: '漂泊者·湮灭',
      segments: [
        { type: 'action', startTime: 0.0, endTime: 2.0, display: 'R', description: '' },
        { type: 'action', startTime: 2.0, endTime: 4.0, display: 'E', description: '' },
        { type: 'switch', time: 4.0, display: '切 - 散华', description: '切人', target: '散华' },
        { type: 'switch', time: 13.0, display: '切 - 散华', description: '切人', target: '散华' },
        { type: 'action', startTime: 16.0, endTime: 17.0, display: 'E', description: '' },
        { type: 'action', startTime: 17.0, endTime: 21.0, display: 'A×3+ 闪避+Q', description: '' },
        { type: 'action', startTime: 21.0, endTime: 22.0, display: 'A×2', description: '' },
        { type: 'action', startTime: 22.0, endTime: 24.0, display: 'R', description: '' },
        { type: 'action', startTime: 24.0, endTime: 28.0, display: 'A×3+ 闪避+Q', description: '' },
      ]
    },
    {
      name: '散华',
      segments: [
        { type: 'action', startTime: 4.0, endTime: 5.0, display: 'E', description: '' },
        { type: 'action', startTime: 5.0, endTime: 8.0, display: 'E+R+ 重击蓄力', description: '' },
        { type: 'switch', time: 8.0, display: '切 - 维里奈', description: '切人', target: '维里奈' },
        { type: 'action', startTime: 13.0, endTime: 15.0, display: 'A×2+Q', description: '' },
        { type: 'switch', time: 15.0, endTime: 16.0, display: '', description: '变奏', target: '漂泊者·湮灭' },
      ]
    },
    {
      name: '维里奈',
      segments: [
        { type: 'action', startTime: 8.0, endTime: 10.0, display: 'E+Q+R', description: '' },
        { type: 'action', startTime: 10.0, endTime: 11.0, display: '跳 A×2', description: '' },
        { type: 'switch', time: 11.0, endTime: 13.0, display: '', description: '变奏', target: '漂泊者·湮灭' },
      ]
    },
  ]
}

const showDialog = ref(false)
const isPlaying = ref(false)
const currentTime = ref(0)
const playerRef = ref<InstanceType<typeof RotationPlayer> | null>(null)
let timer: number | null = null

const currentRotation = computed(() => 启动轴)

const togglePlay = () => {
  if (isPlaying.value) {
    stop()
  } else {
    play()
  }
}

const play = () => {
  isPlaying.value = true
  timer = window.setInterval(() => {
    currentTime.value += 0.016
    if (currentTime.value >= currentRotation.value.totalDuration) {
      currentTime.value = currentRotation.value.totalDuration
      stop()
    }
  }, 16)
}

const stop = () => {
  isPlaying.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

const reset = () => {
  stop()
  currentTime.value = 0
}

const handleSeek = (time: number) => {
  currentTime.value = time
}

watch(showDialog, (newVal) => {
  if (newVal) {
    nextTick(() => {
      playerRef.value?.reset()
    })
  }
})
</script>

<style scoped>
.test-action { display: inline-block; }

.open-btn {
  padding: 12px 24px;
  font-size: 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.open-btn:hover { opacity: 0.9; transform: scale(1.02); }

.overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog {
  background: var(--bg-secondary);
  border-radius: 20px;
  padding: 24px;
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  overflow-y: auto;
  color: var(--text-primary);
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5);
  border: 1px solid var(--border-color);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header h3 { margin: 0; font-size: 20px; font-weight: 600; color: var(--text-primary); }

.close-btn {
  background: var(--bg-tertiary);
  border: none;
  color: var(--text-secondary);
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  transition: all 0.2s;
}
.close-btn:hover { background: var(--bg-primary); color: var(--text-primary); }

.controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.play-btn, .reset-btn {
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-weight: 500;
}
.play-btn { background: #34c759; color: white; }
.play-btn:hover { background: #30d158; }
.reset-btn { background: var(--bg-tertiary); color: var(--text-primary); }
.reset-btn:hover { background: #3a3a3c; }
.time-display {
  margin-left: auto;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
  color: var(--text-secondary);
  font-size: 14px;
}

.fade-enter-active, .fade-leave-active { transition: all 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: scale(0.95); }
</style>