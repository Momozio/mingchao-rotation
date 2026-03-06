<template>
  <div class="rotation-edit">
    <!-- 顶部工具栏 -->
    <div class="edit-header">
      <div class="char-tabs">
        <span class="tab-label">首发角色:</span>
        <button
          v-for="(char, index) in characters"
          :key="char"
          :class="['char-tab', { 
            active: firstCharIndex === index,
            disabled: hasAnyOperations && firstCharIndex !== index
          }]"
          @click="setFirstCharacter(index)"
        >
          <img
            :src="`/assets/characters/${char}.webp`"
            :alt="char"
            @error="$event.target.style.display='none'"
          />
          <span>{{ char }}</span>
        </button>
      </div>
      <div class="header-controls">
        <label class="duration-input">
          总时长:
          <input
            type="number"
            v-model.number="internalDuration"
            max="999"
            min="1"
            class="w-16 px-2 py-1 rounded bg-[var(--bg-primary)] border border-[var(--border-color)] text-[var(--text-primary)]"
          />
          s
        </label>
        <button @click="$emit('save', getRotationData())" class="btn-save">保存</button>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <button
        class="tool-btn"
        @click="addSwitch"
      >
        🔄 切人
      </button>
      <button
        class="tool-btn"
        @click="addVariation"
      >
        🎵 变奏
      </button>
      <div class="current-time">
        当前：{{ currentTime.toFixed(1) }}s
        <button @click="reset" class="btn-reset">↺ 重置</button>
        <button @click="clearAll" class="btn-clear">🗑 清空</button>
      </div>
    </div>

    <!-- 时间轴区域 -->
    <div class="timeline" ref="timelineRef">
      <!-- 顶部总时间轴（带刻度） -->
      <div class="master-timeline-row">
        <div class="row-label master-label invisible"></div>
        <div class="master-timeline" :class="{ dragging: isDraggingMaster }" ref="masterTimelineRef" @mousedown="startDragGlobal">
          <!-- 时间刻度网格 -->
          <div class="time-grid">
            <div
              v-for="s in Math.ceil(internalDuration)"
              :key="'master-grid-' + s"
              class="grid-line"
              :style="{ left: getTimePercent(s - 1) + '%' }"
            ></div>
          </div>
          <div
            v-for="s in Math.ceil(internalDuration)"
            :key="s"
            class="master-scale-label"
            :style="{ left: getTimePercent(s - 1) + '%' }"
          >
            {{ s - 1 }}
          </div>
        </div>
      </div>

      <!-- 角色行 -->
      <div
        v-for="(char, charIndex) in characters"
        :key="char"
        :class="['char-row', { 
          active: activeCharIndex === charIndex,
          'can-interact': activeCharIndex === charIndex
        }]"
        @click="handleRowClick($event, charIndex)"
        @mousedown="handleRowMouseDown($event, charIndex)"
        @mousemove="handleRowMouseMove($event, charIndex)"
        @mouseup="handleRowMouseUp($event, charIndex)"
      >
        <div class="row-label">
          <img
            :src="`/assets/characters/${char}.webp`"
            :alt="char"
            @error="$event.target.style.display='none'"
          />
        </div>
        <div class="row-timeline" :class="{ 
          'interacting': activeCharIndex === charIndex,
          'selecting': isSelecting && activeCharIndex === charIndex
        }">
          <!-- 时间刻度网格 -->
          <div class="time-grid">
            <div
              v-for="s in Math.ceil(internalDuration)"
              :key="'row-grid-' + char + '-' + s"
              class="grid-line"
              :style="{ left: getTimePercent(s - 1) + '%' }"
            ></div>
          </div>
          <!-- 选中区域覆盖层 -->
          <div
            v-if="isSelecting && activeCharIndex === charIndex && selection"
            class="row-selection-overlay"
            :style="{
              left: getTimePercent(selection.start) + '%',
              width: getTimePercent(selection.end - selection.start) + '%'
            }"
          ></div>
          <div class="segments-container">
            <template v-for="(segment, segIndex) in getMergedSegmentsWithVariation(char, getSegments(char))">
              <div
                v-if="segment.type !== 'switch' || segment.isVariationSeg"
                :key="'seg-' + segIndex"
                :class="[
                  'segment-block',
                  segment.type,
                  { 
                    completed: segment.startTime <= currentTime,
                    'is-variation': segment.isVariationSeg
                  }
                ]"
                :style="{
                  left: getTimePercent(segment.startTime) + '%',
                  width: getTimePercent(segment.endTime - segment.startTime) + '%'
                }"
              >
                <span class="segment-label">{{ segment.display }}</span>
              </div>
            </template>
          </div>
          <!-- 切人箭头 -->
          <template v-for="(segment, segIndex) in getSegments(char)" :key="'switch-' + segIndex">
            <div
              v-if="segment.type === 'switch' && !segment.endTime"
              class="switch-arrow-container"
              :class="[getTargetCharIndex(segment.target) < charIndex ? 'arrow-up' : 'arrow-down']"
              :style="{
                left: getTimePercent(segment.startTime) + '%',
                '--arrow-height': (Math.abs(getTargetCharIndex(segment.target) - charIndex) * 72 - 42) + 'px'
              }"
            >
              <div class="switch-arrow-line"></div>
              <img src="/assets/triangle_down_fill.svg" class="switch-arrow-head" />
              <span class="switch-arrow-label">{{ segment.display }}</span>
            </div>
            <div
              v-if="segment.type === 'switch' && segment.endTime"
              class="switch-arrow-container"
              :class="[getTargetCharIndex(segment.target) < charIndex ? 'arrow-up' : 'arrow-down']"
              :style="{
                left: getTimePercent(segment.startTime) + '%',
                '--arrow-height': (Math.abs(getTargetCharIndex(segment.target) - charIndex) * 72 - 42) + 'px'
              }"
            >
              <div class="switch-arrow-line"></div>
              <img src="/assets/triangle_down_fill.svg" class="switch-arrow-head" />
              <span class="switch-arrow-label">变奏 - {{ segment.target }}</span>
            </div>
          </template>
        </div>
      </div>

      <!-- 全局垂直播放头（贯穿所有时间轴，放在最上层） -->
      <div
        class="playhead-overlay"
        :style="{ left: '58px', width: 'calc(100% - 58px)' }"
      >
        <div class="playhead-indicator" :style="{ left: progressPercent + '%' }" :class="{ dragging: isDraggingMaster }">
          <div class="playhead-arrow"></div>
          <div class="playhead-line"></div>
        </div>
        <!-- 吸附高亮指示器 -->
        <div v-if="isSnapping" class="snap-indicator" :style="{ left: getTimePercent(snapPoint) + '%' }">
          <div class="snap-line"></div>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 - Action -->
    <Teleport to="body">
      <div v-if="showActionDialog" class="dialog-overlay" @click.self="closeActionDialog">
        <div class="dialog">
          <h3>添加操作</h3>
          <div class="dialog-content">
            <div class="time-range">
              时间范围：{{ selection?.start.toFixed(1) }}s - {{ selection?.end.toFixed(1) }}s
              ({{ (selection?.end || 0 - selection?.start || 0).toFixed(1) }}s)
            </div>
            <div class="preset-buttons">
              <button @click="selectPreset('E')" class="preset-btn">E</button>
              <button @click="selectPreset('Q')" class="preset-btn">Q</button>
              <button @click="selectPreset('R')" class="preset-btn">R</button>
              <button @click="selectPreset('A')" class="preset-btn">A</button>
              <button @click="selectPreset('闪避')" class="preset-btn">闪避</button>
              <button @click="selectPreset('重击')" class="preset-btn">重击</button>
            </div>
            <div class="form-group">
              <label>显示文本:</label>
              <input v-model="actionForm.display" placeholder="自定义文本" class="form-input" />
            </div>
            <div class="form-group">
              <label>描述:</label>
              <input v-model="actionForm.description" placeholder="可选描述" class="form-input" />
            </div>
          </div>
          <div class="dialog-actions">
            <button @click="closeActionDialog" class="btn-cancel">取消</button>
            <button @click="confirmAction" class="btn-confirm">确定</button>
          </div>
        </div>
      </div>

      <!-- 切人弹窗 -->
      <div v-if="showSwitchDialog" class="dialog-overlay" @click.self="closeSwitchDialog">
        <div class="dialog">
          <h3>选择目标角色</h3>
          <div class="dialog-content">
            <div class="target-characters">
              <button
                v-for="char in getOtherCharacters()"
                :key="char"
                @click="confirmSwitch(char)"
                class="target-char-btn"
              >
                <img
                  :src="`/assets/characters/${char}.webp`"
                  :alt="char"
                  @error="$event.target.style.display='none'"
                />
                <span>{{ char }}</span>
              </button>
            </div>
            <div v-if="switchWarning" class="warning-text">{{ switchWarning }}</div>
          </div>
          <div class="dialog-actions">
            <button @click="closeSwitchDialog" class="btn-cancel">取消</button>
          </div>
        </div>
      </div>

      <!-- 变奏弹窗 -->
      <div v-if="showVariationDialog" class="dialog-overlay" @click.self="closeVariationDialog">
        <div class="dialog">
          <h3>变奏设置</h3>
          <div class="dialog-content">
            <div class="form-group">
              <label>目标角色:</label>
              <select v-model="variationForm.target" class="form-input">
                <option v-for="char in getOtherCharacters()" :key="char" :value="char">
                  {{ char }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>变奏时长 (秒):</label>
              <input
                v-model.number="variationForm.duration"
                type="number"
                step="0.1"
                min="0.1"
                class="form-input"
              />
            </div>
          </div>
          <div class="dialog-actions">
            <button @click="closeVariationDialog" class="btn-cancel">取消</button>
            <button @click="confirmVariation" class="btn-confirm">确定</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Segment {
  type: 'action' | 'switch'
  startTime: number
  endTime?: number
  display: string
  description?: string
  target?: string
}

interface ActionFormData {
  display: string
  description: string
}

interface VariationFormData {
  target: string
  duration: number
}

interface MergedSegment {
  startTime: number
  endTime: number
  display: string
  description: string
  count: number
  type?: 'action' | 'switch'
  isVariationSeg?: boolean
}

const props = defineProps<{
  characters: string[]
  totalDuration?: number
}>()

const emit = defineEmits<{
  save: [data: any]
  cancel: []
}>()

const internalDuration = ref(props.totalDuration || 30)
const firstCharIndex = ref(0) // 首发角色（永远不变，只是标记）
const activeCharIndex = ref(0) // 当前激活的时间轴（切人/变奏会切换）
const currentTime = ref(0)

// 各角色的 segments
const segmentsData = ref<{ [key: string]: Segment[] }>({})

// 监听 characters 变化并初始化
watch(() => props.characters, (newChars) => {
  newChars.forEach(char => {
    if (!segmentsData.value[char]) {
      segmentsData.value[char] = []
    }
  })
}, { immediate: true })

// 切人 CD 记录
const lastSwitchTime = ref<{ [key: string]: number }>({})

// 选择区域
const isSelecting = ref(false)
const selectionStart = ref(0)
const selection = ref<{ start: number; end: number } | null>(null)

// 弹窗状态
const showActionDialog = ref(false)
const showSwitchDialog = ref(false)
const showVariationDialog = ref(false)
const switchWarning = ref('')

// 表单数据
const actionForm = ref<ActionFormData>({ display: '', description: '' })
const variationForm = ref<VariationFormData>({ target: '', duration: 1 })

// 点击位置的时间
const clickTime = ref(0)

// 吸附相关
const snapThreshold = 0.5 // 吸附阈值（秒）
const isSnapping = ref(false)
const snapPoint = ref(0)

const getSegments = (char: string): Segment[] => {
  return segmentsData.value[char] || []
}

// 获取吸附点（所有角色的 segment 边界）
const getSnapPoints = (): number[] => {
  const points: number[] = [0, internalDuration.value]
  props.characters.forEach(char => {
    const segments = segmentsData.value[char] || []
    segments.forEach(seg => {
      if (seg.startTime !== undefined) points.push(seg.startTime)
      if (seg.endTime !== undefined && seg.endTime > seg.startTime) points.push(seg.endTime)
    })
  })
  return [...new Set(points)].sort((a, b) => a - b)
}

// 吸附函数
const snapToPoint = (time: number): number => {
  const snapPoints = getSnapPoints()
  let closestPoint = time
  let minDistance = snapThreshold
  
  for (const point of snapPoints) {
    const distance = Math.abs(time - point)
    if (distance < minDistance) {
      minDistance = distance
      closestPoint = point
    }
  }
  
  isSnapping.value = minDistance < snapThreshold
  snapPoint.value = closestPoint
  
  return closestPoint
}

const getMergedSegments = (segments: Segment[]): MergedSegment[] => {
  const safeSegments = segments ?? []
  const actions = safeSegments.filter(s => s.type === 'action')
  const switches = safeSegments.filter(s => s.type === 'switch')
  
  const merged: MergedSegment[] = []
  let i = 0
  
  while (i < actions.length) {
    const action = actions[i]
    let count = 1
    let endTime = action.endTime || 0
    
    while (i + count < actions.length && 
           actions[i + count].display === action.display &&
           Math.abs((actions[i + count].startTime || 0) - endTime) < 0.3) {
      endTime = actions[i + count].endTime || 0
      count++
    }
    
    merged.push({
      startTime: action.startTime || 0,
      endTime,
      display: count > 1 ? `${count}×${action.display}` : action.display,
      description: action.description || '',
      count,
      type: 'action'
    })
    
    i += count
  }
  
  switches.forEach(sw => {
    const hasEndTime = sw.endTime !== undefined && sw.endTime > (sw.startTime || 0)
    if (hasEndTime) {
      merged.push({
        startTime: sw.startTime || 0,
        endTime: sw.endTime,
        display: `变奏 - ${sw.target}`,
        description: '',
        count: 1,
        type: 'switch'
      })
    }
  })
  
  return merged.sort((a, b) => a.startTime - b.startTime)
}

const getVariationSegments = (characterName: string) => {
  const variationSegs: (MergedSegment & { isVariationSeg: boolean })[] = []
  props.characters.forEach(char => {
    const charSegments = segmentsData.value[char] ?? []
    charSegments.forEach(seg => {
      if (seg.type === 'switch' && seg.endTime && seg.target === characterName) {
        variationSegs.push({
          startTime: seg.startTime || 0,
          endTime: seg.endTime,
          display: '',
          description: '变奏',
          count: 1,
          type: 'action',
          isVariationSeg: true
        })
      }
    })
  })
  return variationSegs
}

const getMergedSegmentsWithVariation = (characterName: string, segments: Segment[]) => {
  const baseSegments = getMergedSegments(segments || [])
  const variationSegs = getVariationSegments(characterName)
  return [...baseSegments, ...variationSegs].sort((a, b) => a.startTime - b.startTime)
}

const getTargetCharIndex = (targetName: string) => {
  return props.characters.findIndex(c => c === targetName)
}

const getTimePercent = (time: number) => {
  return (time / internalDuration.value) * 100
}

const progressPercent = computed(() => {
  return (currentTime.value / internalDuration.value) * 100
})

// 计算播放头所需高度
const playheadHeight = computed(() => {
  const masterHeight = 48 // master-timeline-row 高度
  const rowHeight = 48 // 每个角色行高度
  const rowMargin = 24 // 角色行间距
  const extraLength = 1000 // 向下延伸的长度
  return masterHeight + (props.characters.length * rowHeight) + ((props.characters.length - 1) * rowMargin) + extraLength
})

// 检查是否有操作
const hasAnyOperations = computed(() => {
  return props.characters.some(char => (segmentsData.value[char] || []).length > 0)
})

// 获取其他角色（用于切人/变奏选择）
const getOtherCharacters = () => {
  return props.characters.filter((_, i) => i !== activeCharIndex.value)
}

const setFirstCharacter = (index: number) => {
  // 有操作时禁止切换首发角色
  if (hasAnyOperations.value) {
    return
  }
  firstCharIndex.value = index
}

// 添加切人操作
const addSwitch = () => {
  clickTime.value = currentTime.value
  showSwitchDialog.value = true
  switchWarning.value = ''
}

// 添加变奏操作
const addVariation = () => {
  clickTime.value = currentTime.value
  variationForm.value.target = getOtherCharacters()[0] || ''
  variationForm.value.duration = 1
  showVariationDialog.value = true
}

const reset = () => {
  currentTime.value = 0
}

const clearAll = () => {
  if (confirm('确定要清空所有操作吗？')) {
    props.characters.forEach(char => {
      segmentsData.value[char] = []
    })
    lastSwitchTime.value = {}
    firstCharIndex.value = 0
    activeCharIndex.value = 0
    currentTime.value = 0
  }
}

// 全局播放头拖拽 - 使用 requestAnimationFrame 实现流畅拖动
const masterTimelineRef = ref<HTMLElement | null>(null)
const timelineRef = ref<HTMLElement | null>(null)
const isDraggingMaster = ref(false)
let animationFrameId = 0
let currentClientX = 0

// 更新播放头位置（使用 rAF 批量处理）
const updatePosition = () => {
  if (!isDraggingMaster.value || !masterTimelineRef.value) return
  
  const rect = masterTimelineRef.value.getBoundingClientRect()
  const percent = Math.max(0, Math.min((currentClientX - rect.left) / rect.width, 1))
  currentTime.value = snapToPoint(percent * internalDuration.value)
  
  animationFrameId = requestAnimationFrame(updatePosition)
}

const startDragGlobal = (event: MouseEvent) => {
  isDraggingMaster.value = true
  currentClientX = event.clientX
  animationFrameId = requestAnimationFrame(updatePosition)
  
  // 添加全局事件监听，即使鼠标离开时间轴也能拖动
  window.addEventListener('mousemove', onDragGlobal, { passive: true })
  window.addEventListener('mouseup', endDragGlobal, { once: true })
}

const onDragGlobal = (event: MouseEvent) => {
  currentClientX = event.clientX
}

const endDragGlobal = () => {
  isDraggingMaster.value = false
  isSnapping.value = false
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('mousemove', onDragGlobal)
}

// 行点击/拖动 - 切换首发角色或拖动选择区间
const handleRowClick = (event: MouseEvent, charIndex: number) => {
  // 如果拖动了，不触发点击
  if (isSelecting.value) {
    isSelecting.value = false
    return
  }
  // 有操作时禁止切换首发角色
  if (hasAnyOperations.value && charIndex !== firstCharIndex.value) {
    return
  }
  setFirstCharacter(charIndex)
  // 同时切换激活的时间轴
  activeCharIndex.value = charIndex
}

const handleRowMouseDown = (event: MouseEvent, charIndex: number) => {
  if (charIndex !== activeCharIndex.value) return
  isSelecting.value = true
  selectionStart.value = getTimeFromEvent(event)
  selection.value = { start: selectionStart.value, end: selectionStart.value }
}

const handleRowMouseMove = (event: MouseEvent, charIndex: number) => {
  if (!isSelecting.value || charIndex !== activeCharIndex.value) return
  const endTime = snapToPoint(getTimeFromEvent(event))
  selection.value = {
    start: Math.min(selectionStart.value, endTime),
    end: Math.max(selectionStart.value, endTime)
  }
}

const handleRowMouseUp = (event: MouseEvent, charIndex: number) => {
  if (!isSelecting.value || charIndex !== activeCharIndex.value) return
  isSnapping.value = false
  if (selection.value && selection.value.end - selection.value.start > 0.1) {
    showActionDialog.value = true
    actionForm.value = { display: '', description: '' }
  } else {
    isSelecting.value = false
  }
}

const getTimeFromEvent = (event: MouseEvent): number => {
  const rowTimeline = (event.currentTarget as HTMLElement).querySelector('.row-timeline')
  if (!rowTimeline) return 0
  const rect = rowTimeline.getBoundingClientRect()
  const percent = Math.max(0, Math.min((event.clientX - rect.left) / rect.width, 1))
  return percent * internalDuration.value
}

// Action 弹窗操作
const closeActionDialog = () => {
  showActionDialog.value = false
  selection.value = null
}

const selectPreset = (text: string) => {
  actionForm.value.display = text
}

const confirmAction = () => {
  if (!selection.value || !actionForm.value.display) return
  const char = props.characters[activeCharIndex.value]
  segmentsData.value[char].push({
    type: 'action',
    startTime: selection.value.start,
    endTime: selection.value.end,
    display: actionForm.value.display,
    description: actionForm.value.description
  })
  segmentsData.value[char].sort((a, b) => a.startTime - b.startTime)
  closeActionDialog()
}

// 拖动选择时间范围（用于添加 action，已移除）

// 切人弹窗操作
const closeSwitchDialog = () => {
  showSwitchDialog.value = false
}

const confirmSwitch = (targetChar: string) => {
  const currentChar = props.characters[activeCharIndex.value]
  const lastTime = lastSwitchTime.value[currentChar]
  
  // CD 检查：只有第一次切人后才需要检查 CD
  if (lastTime && clickTime.value - lastTime < 3) {
    switchWarning.value = `切人 CD 中，请等待 ${(3 - (clickTime.value - lastTime)).toFixed(1)}s`
    return
  }
  
  segmentsData.value[currentChar].push({
    type: 'switch',
    startTime: clickTime.value,
    display: `切 - ${targetChar}`,
    target: targetChar
  })
  lastSwitchTime.value[currentChar] = clickTime.value
  segmentsData.value[currentChar].sort((a, b) => a.startTime - b.startTime)
  
  // 切换到目标角色的时间轴
  activeCharIndex.value = props.characters.findIndex(c => c === targetChar)
  
  closeSwitchDialog()
}

// 变奏弹窗操作
const closeVariationDialog = () => {
  showVariationDialog.value = false
}

const confirmVariation = () => {
  const currentChar = props.characters[activeCharIndex.value]
  const endTime = clickTime.value + variationForm.value.duration
  
  segmentsData.value[currentChar].push({
    type: 'switch',
    startTime: clickTime.value,
    endTime: endTime,
    display: '变奏',
    target: variationForm.value.target
  })
  segmentsData.value[currentChar].sort((a, b) => a.startTime - b.startTime)
  
  // 切换到目标角色的时间轴
  activeCharIndex.value = props.characters.findIndex(c => c === variationForm.value.target)
  
  closeVariationDialog()
}

const getRotationData = () => {
  return {
    name: '自定义输出轴',
    totalDuration: internalDuration.value,
    characters: props.characters.map(char => ({
      name: char,
      segments: segmentsData.value[char]
    }))
  }
}
</script>

<style scoped>
.rotation-edit {
  background: var(--bg-tertiary);
  border-radius: 16px;
  padding: 20px;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.rotation-edit * {
  user-select: none;
  -webkit-user-select: none;
}

.rotation-edit input,
.rotation-edit select,
.rotation-edit textarea {
  user-select: text;
  -webkit-user-select: text;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.char-tabs {
  display: flex;
  gap: 8px;
  align-items: center;
}

.tab-label {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.char-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.char-tab.active {
  background: var(--accent-color);
  color: white;
}

.char-tab img {
  width: 28px;
  height: 28px;
  border-radius: 6px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.duration-input {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.btn-save {
  padding: 8px 20px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save:hover {
  opacity: 0.9;
  transform: scale(1.02);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-left: 58px;
}

.tool-btn {
  padding: 8px 16px;
  background: var(--bg-primary);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.tool-btn.active {
  background: var(--accent-color);
  color: white;
}

.current-time {
  margin-left: auto;
  color: var(--text-secondary);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-reset {
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary);
}

.btn-clear {
  padding: 4px 10px;
  background: rgba(255, 59, 48, 0.15);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #ff3b30;
  transition: all 0.2s;
}

.btn-clear:hover {
  background: rgba(255, 59, 48, 0.25);
}

.timeline {
  position: relative;
  padding-top: 8px;
}

.master-timeline-row {
  display: flex;
  align-items: center;
  height: 48px;
  margin-bottom: 8px;
}

.master-label {
  width: 48px;
  flex-shrink: 0;
  background: transparent;
  border-radius: 8px;
  margin-right: 10px;
}

.master-timeline {
  position: relative;
  flex: 1;
  height: 40px;
  background: var(--bg-primary);
  border-radius: 8px;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  transition: all 0.2s;
  border: 2px solid transparent;
  z-index: 10;
}

.master-timeline:hover {
  background: rgba(255, 255, 255, 0.08);
}

.master-timeline.dragging {
  cursor: grabbing;
  border-color: var(--accent-color);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

.master-scale-label {
  position: absolute;
  bottom: 4px;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
  transform: translateX(-50%);
  pointer-events: none;
}

.playhead-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 58px;
  pointer-events: none;
  z-index: 200;
}

.playhead-indicator {
  position: absolute;
  top: 22px;
  bottom: 0;
  width: 2px;
  transform: translateX(-50%);
  pointer-events: none;
  transition: width 0.15s;
}

.playhead-indicator.dragging {
  width: 3px;
}

/* 吸附指示器 */
.snap-indicator {
  position: absolute;
  top: 22px;
  bottom: 0;
  pointer-events: none;
  z-index: 150;
}

.snap-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  transform: translateX(-50%);
  background: #00d4ff;
  box-shadow: 0 0 8px #00d4ff, 0 0 15px rgba(0, 212, 255, 0.5);
  border-radius: 1px;
}

/* 顶部朝下的三角形箭头 */
.playhead-arrow {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 8px solid rgba(255, 255, 255, 0.9);
  transition: all 0.15s;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

/* 垂直线条 */
.playhead-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  background: rgba(255, 255, 255, 0.6);
  transition: all 0.15s;
}

.playhead-indicator.dragging .playhead-arrow {
  border-top-color: var(--accent-color);
  filter: drop-shadow(0 0 6px var(--accent-color));
}

.playhead-indicator.dragging .playhead-line {
  background: var(--accent-color);
  box-shadow: 0 0 15px var(--accent-color);
}

.master-timeline-row {
  display: flex;
  align-items: center;
  height: 48px;
  margin-bottom: 8px;
}

.master-label {
  width: 48px;
  flex-shrink: 0;
  background: transparent;
  border-radius: 8px;
  margin-right: 10px;
}

.master-timeline {
  position: relative;
  flex: 1;
  height: 40px;
  background: var(--bg-primary);
  border-radius: 8px;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  transition: all 0.2s;
  border: 2px solid transparent;
  z-index: 10;
}

.master-timeline:hover {
  background: rgba(255, 255, 255, 0.08);
}

.master-timeline.dragging {
  cursor: grabbing;
  border-color: var(--accent-color);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

.master-timeline {
  overflow: visible;
}

/* 时间网格 */
.master-timeline .time-grid,
.row-timeline .time-grid {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  pointer-events: none;
  z-index: 1;
}

.master-timeline .grid-line,
.row-timeline .grid-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(255, 255, 255, 0.06);
  pointer-events: none;
}

.master-playhead {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 2px;
  transform: translateX(-50%);
  pointer-events: none;
  z-index: 100;
  transition: all 0.15s;
}

.master-playhead.dragging::before {
  background: var(--accent-color);
  box-shadow: 0 0 10px var(--accent-color);
}

.master-playhead::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  background: rgba(255, 255, 255, 1);
  transition: all 0.15s;
}

.master-playhead-handle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 10px solid white;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.master-scale-label {
  position: absolute;
  bottom: 4px;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
  transform: translateX(-50%);
  pointer-events: none;
}

/* 播放头轨道 - 贯穿整个时间轴区域 */
.master-playhead-track {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 58px;
  pointer-events: none;
  z-index: 100;
}

.master-playhead {
  position: absolute;
  top: 22px;
  bottom: 0;
  width: 2px;
  background: transparent;
  transform: translateX(-50%);
  pointer-events: none;
  transition: all 0.15s;
}

.master-playhead.dragging {
  width: 3px;
}

/* 顶部朝下的三角形箭头 */
.master-playhead::before {
  content: '';
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 8px solid rgba(255, 255, 255, 0.8);
  transition: all 0.15s;
}

/* 播放头线条 */
.master-playhead::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  background: rgba(255, 255, 255, 0.6);
  transition: all 0.15s;
}

.master-playhead.dragging::before {
  border-top-color: var(--accent-color);
  filter: drop-shadow(0 0 4px var(--accent-color));
}

.master-playhead.dragging::after {
  background: var(--accent-color);
  box-shadow: 0 0 15px var(--accent-color);
}

.char-row {
  display: flex;
  align-items: center;
  height: 48px;
  margin-bottom: 24px;
  cursor: pointer;
  position: relative;
}

.char-row:last-child {
  margin-bottom: 0;
}

.char-row.active .row-label {
  background: var(--accent-color);
}

.row-label {
  width: 48px;
  flex-shrink: 0;
  background: var(--bg-primary);
  border-radius: 8px;
  margin-right: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  transition: all 0.2s;
}

.row-label img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
}

.row-timeline {
  position: relative;
  flex: 1;
  height: 36px;
  background: var(--bg-primary);
  border-radius: 8px;
  overflow: visible;
  transition: all 0.2s;
  border: 2px solid transparent;
  z-index: 1;
}

/* 只有激活且可交互的角色行才有 hover 效果 */
.char-row.can-interact:hover .row-timeline.interacting {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  cursor: pointer;
}

/* 正在选择区域时的效果 */
.char-row.can-interact .row-timeline.selecting {
  background: rgba(255, 255, 255, 0.12);
  border-color: var(--accent-color);
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
}

/* 不可用的首发角色按钮（有操作时禁止点击切换） */
.char-tab.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.char-tab.disabled:hover {
  background: var(--bg-primary);
  border-color: transparent;
}

/* 选中区域覆盖层 */
.row-selection-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  background: var(--accent-color);
  opacity: 0.3;
  border-radius: 6px;
  pointer-events: none;
  z-index: 1;
}

.segments-container {
  position: absolute;
  top: 4px;
  left: 0;
  right: 0;
  bottom: 4px;
  z-index: 2;
  overflow: visible;
}

.segment-block {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 9px;
  white-space: nowrap;
  background: #636366;
  z-index: 1;
}

.segment-block.completed {
  background: #34c759;
}

.segment-block.switch {
  background: #ff7f16;
}

.segment-block.is-variation {
  background: #ff9500;
  opacity: 0.7;
}

.segment-label {
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  padding: 0 4px;
}

.switch-arrow-container {
  position: absolute;
  top: 100%;
  left: 0;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 200;
  pointer-events: none;
}

.switch-arrow-container.arrow-up {
  top: auto;
  bottom: 100%;
  flex-direction: column-reverse;
}

.switch-arrow-line {
  width: 2px;
  background: #ff7f16;
  height: var(--arrow-height, 16px);
  flex-shrink: 0;
}

.switch-arrow-container.arrow-up .switch-arrow-line {
  height: var(--arrow-height, 16px);
  margin-top: -4px;
}

.switch-arrow-container.arrow-down .switch-arrow-line {
  height: var(--arrow-height, 16px);
  margin-bottom: -4px;
}

.switch-arrow-head {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.switch-arrow-container.arrow-up .switch-arrow-head {
  transform: rotate(180deg);
}

.switch-arrow-label {
  font-size: 11px;
  color: #ff7f16;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  white-space: nowrap;
  font-weight: 500;
  position: absolute;
  left: 14px;
  bottom: 0px;
}

.switch-arrow-container.arrow-up .switch-arrow-label {
  left: 14px;
  top: 0px;
  bottom: auto;
}

/* Dialog styles */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 24px;
  width: 90%;
  max-width: 450px;
  color: var(--text-primary);
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5);
  border: 1px solid var(--border-color);
}

.dialog h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
}

.dialog-content {
  margin-bottom: 20px;
}

.time-range {
  background: var(--bg-primary);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.preset-btn {
  padding: 8px 16px;
  background: var(--bg-tertiary);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: var(--accent-color);
  color: white;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.target-characters {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.target-char-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-primary);
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.target-char-btn:hover {
  border-color: var(--accent-color);
  background: var(--bg-tertiary);
}

.target-char-btn img {
  width: 40px;
  height: 40px;
  border-radius: 8px;
}

.warning-text {
  color: #ff3b30;
  font-size: 14px;
  margin-top: 12px;
  padding: 8px;
  background: rgba(255, 59, 48, 0.1);
  border-radius: 6px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-confirm {
  background: var(--accent-color);
  color: white;
}
</style>
