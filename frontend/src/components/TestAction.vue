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
  name: '守岸人 + 琳奈 + 优诺 - 启动轴 (25s)',
  totalDuration: 25,
  characters: [
    {
      name: '守岸人',
      segments: [
        { type: 'action', startTime: 0.0, endTime: 0.7, display: 'A', description: '普攻第1段' },
        { type: 'action', startTime: 0.7, endTime: 1.3, display: 'A', description: '普攻第2段' },
        { type: 'action', startTime: 1.3, endTime: 1.9, display: 'A', description: '普攻第3段' },
        { type: 'action', startTime: 1.9, endTime: 2.3, display: 'E', description: '共鸣技能' },
        { type: 'action', startTime: 2.3, endTime: 2.9, display: 'A', description: '普攻第1段' },
        { type: 'action', startTime: 2.9, endTime: 3.5, display: 'A', description: '普攻第2段' },
        { type: 'action', startTime: 3.5, endTime: 4.1, display: 'A', description: '普攻第3段' },
        { type: 'action', startTime: 4.1, endTime: 4.6, display: 'z', description: '重击' },
        { type: 'action', startTime: 4.6, endTime: 5.1, display: 'Q', description: '大招-暴击/爆伤光环+回血' },
        { type: 'switch', time: 5.1, display: '变奏-琳奈', description: '变奏入场', target: '琳奈' },
      ]
    },
    {
      name: '琳奈',
      segments: [
        { type: 'action', startTime: 5.1, endTime: 5.6, display: 'E', description: '技能-伤害加成' },
        { type: 'action', startTime: 5.6, endTime: 6.1, display: 'Q', description: '大招-全队增伤' },
        { type: 'action', startTime: 6.1, endTime: 8.1, display: '长按A长按A长按A长按A长按A', description: '绮彩巡游-轮滑状态' },
        { type: 'action', startTime: 8.1, endTime: 9.1, display: '跳×3', description: '空中跳跃-攒能量' },
        { type: 'action', startTime: 9.1, endTime: 9.6, display: 'A', description: '强化普攻-视觉冲击/虹彩飞溅' },
        { type: 'switch', time: 9.6, display: '切-尤诺', description: '切人', target: '尤诺' },
      ]
    },
    {
      name: '尤诺',
      segments: [
        { type: 'action', startTime: 9.6, endTime: 10.1, display: 'Q', description: '大招-爆发状态' },
        { type: 'action', startTime: 10.1, endTime: 10.6, display: 'E', description: '小技能' },
        { type: 'action', startTime: 10.6, endTime: 10.9, display: '闪', description: '闪避' },
        { type: 'action', startTime: 10.9, endTime: 11.5, display: 'A', description: '普攻' },
        { type: 'action', startTime: 11.5, endTime: 12.0, display: 'A', description: '普攻' },
        { type: 'action', startTime: 12.0, endTime: 12.5, display: 'E', description: '共鸣技能' },
        { type: 'action', startTime: 12.5, endTime: 13.0, display: '跳', description: '跳跃' },
        { type: 'action', startTime: 13.0, endTime: 13.4, display: 'A', description: '普攻' },
        { type: 'action', startTime: 13.4, endTime: 13.7, display: '闪', description: '闪避' },
        { type: 'action', startTime: 13.7, endTime: 14.2, display: 'A', description: '普攻' },
        { type: 'action', startTime: 14.2, endTime: 14.7, display: 'E', description: '强化E' },
        { type: 'action', startTime: 14.7, endTime: 15.2, display: 'A', description: '普攻' },
        { type: 'action', startTime: 15.2, endTime: 15.7, display: 'A', description: '普攻' },
        { type: 'action', startTime: 15.7, endTime: 16.2, display: 'E', description: '共鸣技能' },
        { type: 'action', startTime: 16.2, endTime: 16.7, display: 'A', description: '普攻' },
        { type: 'action', startTime: 16.7, endTime: 17.2, display: 'A', description: '普攻' },
        { type: 'action', startTime: 17.2, endTime: 17.7, display: 'E', description: '共鸣技能' },
        { type: 'action', startTime: 17.7, endTime: 18.2, display: 'A', description: '普攻' },
        { type: 'action', startTime: 18.2, endTime: 18.7, display: 'A', description: '普攻' },
        { type: 'action', startTime: 18.7, endTime: 19.2, display: 'E', description: '共鸣技能' },
        { type: 'action', startTime: 19.2, endTime: 19.7, display: 'A', description: '普攻' },
        { type: 'action', startTime: 19.7, endTime: 20.2, display: 'A', description: '普攻' },
        { type: 'action', startTime: 20.2, endTime: 20.7, display: 'E', description: '共鸣技能' },
        { type: 'action', startTime: 20.7, endTime: 21.2, display: 'A', description: '普攻' },
        { type: 'action', startTime: 21.2, endTime: 21.7, display: 'A', description: '普攻' },
        { type: 'action', startTime: 21.7, endTime: 22.2, display: 'E', description: '共鸣技能' },
        { type: 'action', startTime: 22.2, endTime: 23.0, display: 'R', description: '重击-至臻的完满-满月领域' },
        { type: 'switch', time: 23.0, display: '切-守岸人', description: '切回守岸人', target: '守岸人' },
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