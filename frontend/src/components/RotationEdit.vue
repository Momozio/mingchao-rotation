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
      <button class="tool-btn" @click="addSwitch">🔄 切人</button>
      <button class="tool-btn" @click="addVariation">🎵 变奏</button>
      <div class="current-time">
        当前：{{ currentTime.toFixed(1) }}s
        <button @click="reset" class="btn-reset">↺ 重置</button>
        <button @click="clearAll" class="btn-clear">🗑 清空</button>
      </div>
    </div>

    <!-- 时间轴区域 -->
    <div class="timeline" ref="timelineRef">
      <div class="master-timeline-row">
        <div class="row-label master-label invisible"></div>
        <div class="master-timeline" :class="{ dragging: isDraggingMaster }" ref="masterTimelineRef" @mousedown="startDragGlobal">
          <div class="time-grid">
            <div v-for="s in Math.ceil(internalDuration)" :key="'master-grid-' + s" class="grid-line" :style="{ left: getTimePercent(s - 1) + '%' }"></div>
          </div>
          <div v-for="s in Math.ceil(internalDuration)" :key="s" class="master-scale-label" :style="{ left: getTimePercent(s - 1) + '%' }">{{ s - 1 }}</div>
        </div>
      </div>

      <div v-for="(char, charIndex) in characters" :key="char" :class="['char-row', { active: activeCharIndex === charIndex, 'can-interact': activeCharIndex === charIndex }]" @click="handleRowClick($event, charIndex)" @mousedown="handleRowMouseDown($event, charIndex)" @mousemove="handleRowMouseMove($event, charIndex)" @mouseup="handleRowMouseUp($event, charIndex)" @mouseleave="handleRowMouseLeave($event, charIndex)">
        <div class="row-label">
          <img :src="`/assets/characters/${char}.webp`" :alt="char" @error="$event.target.style.display='none'" />
        </div>
        <div class="row-timeline" :class="{ 'interacting': activeCharIndex === charIndex, 'selecting': isSelecting && activeCharIndex === charIndex }">
          <div class="time-grid">
            <div v-for="s in Math.ceil(internalDuration)" :key="'row-grid-' + char + '-' + s" class="grid-line" :style="{ left: getTimePercent(s - 1) + '%' }"></div>
          </div>
          <div v-if="isSelecting && activeCharIndex === charIndex && selection" class="row-selection-overlay" :style="{ left: getTimePercent(selection.start) + '%', width: getTimePercent(selection.end - selection.start) + '%' }"></div>
          <div class="segments-container">
            <template v-for="(segment, segIndex) in getMergedSegmentsWithVariation(char, getSegments(char))">
              <div v-if="segment.type !== 'switch' || segment.isVariationSeg" :key="'seg-' + segIndex" :class="['segment-block', segment.type, { completed: segment.startTime <= currentTime, 'is-variation': segment.isVariationSeg }]" :style="{ left: getTimePercent(segment.startTime) + '%', width: getTimePercent(segment.endTime - segment.startTime) + '%' }">
                <span class="segment-label">{{ segment.display }}</span>
              </div>
            </template>
          </div>
          <template v-for="(segment, segIndex) in getSegments(char)" :key="'switch-' + segIndex">
            <div v-if="segment.type === 'switch' && !segment.endTime" class="switch-arrow-container" :class="[getTargetCharIndex(segment.target) < charIndex ? 'arrow-up' : 'arrow-down']" :style="{ left: getTimePercent(segment.startTime) + '%', '--arrow-height': (Math.abs(getTargetCharIndex(segment.target) - charIndex) * 72 - 42) + 'px' }">
              <div class="switch-arrow-line"></div>
              <img src="/assets/triangle_down_fill.svg" class="switch-arrow-head" />
              <span class="switch-arrow-label">{{ segment.display }}</span>
            </div>
            <div v-if="segment.type === 'switch' && segment.endTime" class="switch-arrow-container" :class="[getTargetCharIndex(segment.target) < charIndex ? 'arrow-up' : 'arrow-down']" :style="{ left: getTimePercent(segment.startTime) + '%', '--arrow-height': (Math.abs(getTargetCharIndex(segment.target) - charIndex) * 72 - 42) + 'px' }">
              <div class="switch-arrow-line"></div>
              <img src="/assets/triangle_down_fill.svg" class="switch-arrow-head" />
              <span class="switch-arrow-label">变奏 - {{ segment.target }}</span>
            </div>
          </template>
          <div v-if="isMouseSnapping && activeCharIndex === charIndex" class="mouse-snap-indicator" :style="{ left: getTimePercent(mouseSnapPoint) + '%' }">
            <div class="mouse-snap-line"></div>
          </div>
        </div>
      </div>

      <div class="playhead-overlay" :style="{ left: '58px', width: 'calc(100% - 58px)' }">
        <div class="playhead-indicator" :style="{ left: progressPercent + '%' }" :class="{ dragging: isDraggingMaster }">
          <div class="playhead-arrow"></div>
          <div class="playhead-line"></div>
        </div>
        <div v-if="isSnapping" class="snap-indicator" :style="{ left: getTimePercent(snapPoint) + '%' }">
          <div class="snap-line"></div>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <Teleport to="body">
      <!-- Action 弹窗 -->
      <div v-if="showActionDialog" class="dialog-overlay" @click.self="closeActionDialog">
        <div class="dialog">
          <h3>添加操作</h3>
          <div class="dialog-content">
            <div class="time-range">时间范围：{{ selection?.start.toFixed(1) }}s - {{ selection?.end.toFixed(1) }}s ({{ (selection?.end || 0 - selection?.start || 0).toFixed(1) }}s)</div>
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
              <button v-for="char in getOtherCharacters()" :key="char" @click="confirmSwitch(char)" class="target-char-btn">
                <img :src="`/assets/characters/${char}.webp`" :alt="char" @error="$event.target.style.display='none'" />
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
              <div class="target-characters">
                <button v-for="char in getOtherCharacters()" :key="char" @click="variationForm.target = char" :class="['target-char-btn', { active: variationForm.target === char }]">
                  <img :src="`/assets/characters/${char}.webp`" :alt="char" @error="$event.target.style.display='none'" />
                  <span>{{ char }}</span>
                </button>
              </div>
            </div>
            <div class="form-group">
              <label>变奏时长 (秒):</label>
              <input v-model.number="variationForm.duration" type="number" step="0.1" min="0.1" class="form-input" />
            </div>
          </div>
          <div class="dialog-actions">
            <button @click="closeVariationDialog" class="btn-cancel">取消</button>
            <button @click="confirmVariation" class="btn-confirm">确定</button>
          </div>
        </div>
      </div>

      <!-- 全屏裁剪弹窗 -->
      <div v-if="isCroppingMode" class="cropping-overlay" @click.self="cancelCrop">
        <div class="cropping-panel">
          <div class="cropping-title">
            <h4>裁剪视频</h4>
            <p class="cropping-hint">拖动进度条选择开始时间，截取后续 {{ internalDuration }}s</p>
          </div>
          <div class="cropping-area">
            <div class="video-preview-wrapper">
              <video ref="croppingPreviewRef" :src="videoUrl" class="cropping-video" @timeupdate="handlePreviewTimeUpdate" @click="seekVideo"></video>
            </div>
            <div class="progress-container">
              <div class="progress-track" @click="seekByClick">
                <div class="progress-highlight" :style="{ left: startTimePercent + '%', width: durationPercent + '%' }"></div>
              </div>
              <input type="range" :min="0" :max="Math.max(0, videoDuration - internalDuration)" step="0.1" v-model.number="clipStartTime" @input="onClipStartTimeChange" class="progress-slider" />
              <div class="time-labels">
                <span class="time-label start-label">开始：{{ (clipStartTime || 0).toFixed(1) }}s</span>
                <span class="time-label end-label">结束：{{ ((clipStartTime || 0) + internalDuration).toFixed(1) }}s</span>
              </div>
              <div class="interval-playback-bar" :style="{ left: startTimePercent + '%', width: durationPercent + '%' }">
                <div class="playback-controls">
                  <button class="control-btn" @click="startIntervalPreview" :title="!isIntervalPlaying ? '播放区间' : '暂停播放'">{{ !isIntervalPlaying ? '▶' : '⏸' }}</button>
                  <button class="control-btn" @click="stopIntervalPreview">⏹</button>
                  <button class="control-btn" @click="resetInterval" title="重置到区间起点">↺</button>
                </div>
              </div>
            </div>
            <div class="cropping-buttons">
              <button @click="cancelCrop" class="btn-cancel-crop">✕ 取消</button>
              <button @click="cropAndUpload" class="btn-confirm-crop" :disabled="isProcessing">{{ isProcessing ? '处理中...' : '✔ 确认裁剪' }}</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 视频上传区域 -->
    <div class="video-section">
      <div class="video-header">
        <h3>视频上传</h3>
        <button v-if="videoUrl && !isCroppingMode" @click="clearVideo" class="btn-clear-video">清除视频</button>
      </div>
      <div v-if="!videoUrl" class="video-upload" @click="triggerVideoUpload">
        <input type="file" accept="video/*" @change="handleVideoUpload" ref="videoInputRef" class="video-input" />
        <div class="upload-hint">
          <span class="upload-icon">📹</span>
          <span>点击上传视频</span>
        </div>
      </div>
    </div>

    <!-- 已上传视频的正常播放模式 -->
    <div v-if="videoUrl && !isCroppingMode" class="video-preview">
      <video ref="videoRef" :src="videoUrl" class="video-player" @loadedmetadata="handleVideoLoaded" @timeupdate="handleVideoTimeUpdate" @ended="handleVideoEnded"></video>
      <div class="video-controls">
        <div class="video-buttons">
          <label class="sync-play">
            <input type="checkbox" v-model="syncPlay" />
            同步播放
          </label>
          <button @click="toggleVideoPlay" class="btn-video-play">{{ isVideoPlaying ? '⏸ 暂停' : '▶ 播放' }}</button>
          <button @click="resetVideo" class="btn-video-reset">↺ 重置</button>
        </div>
        <div class="video-progress">视频：{{ currentVideoTime.toFixed(1) }}s / {{ videoDuration.toFixed(1) }}s</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { FFmpeg } from '@ffmpeg/ffmpeg'
import { fetchFile } from '@ffmpeg/util'

interface Segment { type: 'action' | 'switch'; startTime: number; endTime?: number; display: string; description?: string; target?: string }
interface ActionFormData { display: string; description: string }
interface VariationFormData { target: string; duration: number }
interface MergedSegment { startTime: number; endTime: number; display: string; description: string; count: number; type?: 'action' | 'switch'; isVariationSeg?: boolean }

const props = defineProps<{ characters: string[]; totalDuration?: number }>()
const emit = defineEmits<{ save: [data: any]; cancel: [] }>()

const internalDuration = ref(props.totalDuration || 30)
const firstCharIndex = ref(0)
const activeCharIndex = ref(0)
const currentTime = ref(0)
const segmentsData = ref<{ [key: string]: Segment[] }>({})

watch(() => props.characters, (newChars) => {
  newChars.forEach(char => { if (!segmentsData.value[char]) segmentsData.value[char] = [] })
}, { immediate: true })

const lastSwitchTime = ref<number | null>(null)
const isSelecting = ref(false)
const selectionStart = ref(0)
const selection = ref<{ start: number; end: number } | null>(null)
const showActionDialog = ref(false)
const showSwitchDialog = ref(false)
const showVariationDialog = ref(false)
const switchWarning = ref('')
const actionForm = ref<ActionFormData>({ display: '', description: '' })
const variationForm = ref<VariationFormData>({ target: '', duration: 1 })
const clickTime = ref(0)

// 视频相关
const videoUrl = ref<string | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)
const videoInputRef = ref<HTMLInputElement | null>(null)
const videoDuration = ref(0)
const clipStartTime = ref(0)
const currentVideoTime = ref(0)
const isVideoPlaying = ref(false)
const syncPlay = ref(false)
const isProcessing = ref(false)
const isCroppingMode = ref(false)
const isIntervalPlaying = ref(false)
let intervalFrameId: number | null = null
const croppingPreviewRef = ref<HTMLVideoElement | null>(null)
const ffmpeg = new FFmpeg()
const ffmpegLoaded = ref(false)

const snapThreshold = 0.2
const isSnapping = ref(false)
const snapPoint = ref(0)
const isMouseSnapping = ref(false)
const mouseSnapPoint = ref(0)

const getSegments = (char: string): Segment[] => segmentsData.value[char] || []

const getSnapPoints = (): number[] => {
  const points: number[] = [0, internalDuration.value]
  props.characters.forEach(char => {
    (segmentsData.value[char] || []).forEach(seg => {
      if (seg.startTime !== undefined) points.push(seg.startTime)
      if (seg.endTime !== undefined && seg.endTime > seg.startTime) points.push(seg.endTime)
    })
  })
  return [...new Set(points)].sort((a, b) => a - b)
}

const snapToPoint = (time: number): number => {
  const snapPoints = getSnapPoints()
  let closestPoint = time
  let minDistance = snapThreshold
  for (const point of snapPoints) {
    const distance = Math.abs(time - point)
    if (distance < minDistance) { minDistance = distance; closestPoint = point }
  }
  isSnapping.value = minDistance < snapThreshold
  snapPoint.value = closestPoint
  return closestPoint
}

const getCurrentCharSnapPoints = (): number[] => {
  const points: number[] = [0, internalDuration.value]
  const currentChar = props.characters[activeCharIndex.value]
  (segmentsData.value[currentChar] || []).forEach(seg => {
    if (seg.startTime !== undefined) points.push(seg.startTime)
    if (seg.endTime !== undefined && seg.endTime > seg.startTime) points.push(seg.endTime)
  })
  props.characters.forEach(char => {
    (segmentsData.value[char] || []).forEach(seg => {
      if (seg.type === 'switch' && seg.endTime) { points.push(seg.startTime); points.push(seg.endTime) }
    })
  })
  return [...new Set(points)].sort((a, b) => a - b)
}

const snapMouseToPoint = (time: number): number => {
  const snapPoints = getCurrentCharSnapPoints()
  let closestPoint = time
  let minDistance = snapThreshold
  for (const point of snapPoints) {
    const distance = Math.abs(time - point)
    if (distance < minDistance) { minDistance = distance; closestPoint = point }
  }
  isMouseSnapping.value = minDistance < snapThreshold
  mouseSnapPoint.value = closestPoint
  return closestPoint
}

const getMergedSegments = (segments: Segment[]): MergedSegment[] => {
  const safeSegments = segments ?? []
  const actions = safeSegments.filter(s => s.type === 'action')
  const switches = safeSegments.filter(s => s.type === 'switch')
  const merged: MergedSegment[] = []
  actions.forEach(action => {
    merged.push({ startTime: action.startTime || 0, endTime: action.endTime || 0, display: action.display, description: action.description || '', count: 1, type: 'action' })
  })
  switches.forEach(sw => {
    const hasEndTime = sw.endTime !== undefined && sw.endTime > (sw.startTime || 0)
    if (hasEndTime) { merged.push({ startTime: sw.startTime || 0, endTime: sw.endTime, display: `变奏 - ${sw.target}`, description: '', count: 1, type: 'switch' }) }
  })
  return merged.sort((a, b) => a.startTime - b.startTime)
}

const getVariationSegments = (characterName: string) => {
  const variationSegs: (MergedSegment & { isVariationSeg: boolean })[] = []
  props.characters.forEach(char => {
    (segmentsData.value[char] ?? []).forEach(seg => {
      if (seg.type === 'switch' && seg.endTime && seg.target === characterName) {
        variationSegs.push({ startTime: seg.startTime || 0, endTime: seg.endTime, display: '', description: '变奏', count: 1, type: 'action', isVariationSeg: true })
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

const getTargetCharIndex = (targetName: string) => props.characters.findIndex(c => c === targetName)
const getTimePercent = (time: number) => (time / internalDuration.value) * 100
const progressPercent = computed(() => (currentTime.value / internalDuration.value) * 100)
const hasAnyOperations = computed(() => props.characters.some(char => (segmentsData.value[char] || []).length > 0))
const getOtherCharacters = () => props.characters.filter((_, i) => i !== activeCharIndex.value)

const setFirstCharacter = (index: number) => { if (!hasAnyOperations.value) firstCharIndex.value = index }
const addSwitch = () => { clickTime.value = currentTime.value; showSwitchDialog.value = true; switchWarning.value = '' }
const addVariation = () => { clickTime.value = currentTime.value; variationForm.value.target = getOtherCharacters()[0] || ''; variationForm.value.duration = 1; showVariationDialog.value = true }
const reset = () => { currentTime.value = 0 }

const clearAll = () => {
  if (confirm('确定要清空所有操作吗？')) {
    props.characters.forEach(char => { segmentsData.value[char] = [] })
    lastSwitchTime.value = null
    firstCharIndex.value = 0
    activeCharIndex.value = 0
    currentTime.value = 0
  }
}

// 全局播放头拖拽
const masterTimelineRef = ref<HTMLElement | null>(null)
const timelineRef = ref<HTMLElement | null>(null)
const isDraggingMaster = ref(false)
let animationFrameId = 0
let currentClientX = 0

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
  window.addEventListener('mousemove', onDragGlobal, { passive: true })
  window.addEventListener('mouseup', endDragGlobal, { once: true })
}
const onDragGlobal = (event: MouseEvent) => { currentClientX = event.clientX }
const endDragGlobal = () => {
  isDraggingMaster.value = false
  isSnapping.value = false
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('mousemove', onDragGlobal)
}

const handleRowClick = (event: MouseEvent, charIndex: number) => {
  if (isSelecting.value) return
  if (hasAnyOperations.value && charIndex !== firstCharIndex.value) return
  if (!hasAnyOperations.value) { setFirstCharacter(charIndex); activeCharIndex.value = charIndex }
}

const handleRowMouseDown = (event: MouseEvent, charIndex: number) => {
  if (charIndex !== activeCharIndex.value) return
  isSelecting.value = true
  selectionStart.value = snapMouseToPoint(getTimeFromEvent(event))
  selection.value = { start: selectionStart.value, end: selectionStart.value }
}

const handleRowMouseMove = (event: MouseEvent, charIndex: number) => {
  if (charIndex !== activeCharIndex.value) return
  if (isSelecting.value) {
    const endTime = getTimeFromEvent(event)
    selection.value = { start: Math.min(selectionStart.value, endTime), end: Math.max(selectionStart.value, endTime) }
  } else { snapMouseToPoint(getTimeFromEvent(event)) }
}

const handleRowMouseLeave = (event: MouseEvent, charIndex: number) => { if (charIndex !== activeCharIndex.value) return; isMouseSnapping.value = false }

const handleRowMouseUp = (event: MouseEvent, charIndex: number) => {
  if (!isSelecting.value || charIndex !== activeCharIndex.value) return
  isSnapping.value = false
  if (selection.value && selection.value.end - selection.value.start > 0.1) { showActionDialog.value = true; actionForm.value = { display: '', description: '' } }
  else { isSelecting.value = false }
}

const getTimeFromEvent = (event: MouseEvent): number => {
  const rowTimeline = (event.currentTarget as HTMLElement).querySelector('.row-timeline')
  if (!rowTimeline) return 0
  const rect = rowTimeline.getBoundingClientRect()
  const percent = Math.max(0, Math.min((event.clientX - rect.left) / rect.width, 1))
  return percent * internalDuration.value
}

const closeActionDialog = () => { showActionDialog.value = false; selection.value = null }
const selectPreset = (text: string) => { actionForm.value.display = text }

const confirmAction = () => {
  if (!selection.value || !actionForm.value.display) return
  const char = props.characters[activeCharIndex.value]
  segmentsData.value[char].push({ type: 'action', startTime: selection.value.start, endTime: selection.value.end, display: actionForm.value.display, description: actionForm.value.description })
  segmentsData.value[char].sort((a, b) => a.startTime - b.startTime)
  closeActionDialog()
}

const closeSwitchDialog = () => { showSwitchDialog.value = false }

const confirmSwitch = (targetChar: string) => {
  const lastTime = lastSwitchTime.value
  if (lastTime !== null && clickTime.value - lastTime < 3) {
    switchWarning.value = `切人 CD 中，请等待 ${(3 - (clickTime.value - lastTime)).toFixed(1)}s`
    return
  }
  const currentChar = props.characters[activeCharIndex.value]
  segmentsData.value[currentChar].push({ type: 'switch', startTime: clickTime.value, display: `切 - ${targetChar}`, target: targetChar })
  lastSwitchTime.value = clickTime.value
  segmentsData.value[currentChar].sort((a, b) => a.startTime - b.startTime)
  activeCharIndex.value = props.characters.findIndex(c => c === targetChar)
  closeSwitchDialog()
}

const closeVariationDialog = () => { showVariationDialog.value = false }

const confirmVariation = () => {
  const currentChar = props.characters[activeCharIndex.value]
  const endTime = clickTime.value + variationForm.value.duration
  segmentsData.value[currentChar].push({ type: 'switch', startTime: clickTime.value, endTime, display: '变奏', target: variationForm.value.target })
  segmentsData.value[currentChar].sort((a, b) => a.startTime - b.startTime)
  activeCharIndex.value = props.characters.findIndex(c => c === variationForm.value.target)
  closeVariationDialog()
}

const getRotationData = () => ({ name: '自定义输出轴', totalDuration: internalDuration.value, characters: props.characters.map(char => ({ name: char, segments: segmentsData.value[char] })) })

// 视频相关函数
const triggerVideoUpload = () => { videoInputRef.value?.click() }

const handleVideoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const url = URL.createObjectURL(file)
  videoUrl.value = url
  const tempVideo = document.createElement('video')
  tempVideo.src = url
  await new Promise<void>((resolve) => {
    tempVideo.onloadedmetadata = () => {
      videoDuration.value = tempVideo.duration
      if (videoDuration.value < internalDuration.value) {
        alert(`视频时长 (${videoDuration.value.toFixed(1)}s) 小于轴时长 (${internalDuration.value}s)，请上传更长的视频`)
        isCroppingMode.value = false
        videoUrl.value = null
        resolve()
        return
      }
      clipStartTime.value = 0
      isCroppingMode.value = true
      resolve()
    }
  })
}

const handleVideoLoaded = () => { if (videoRef.value) { videoDuration.value = videoRef.value.duration; clipStartTime.value = 0 } }

const handleVideoTimeUpdate = () => {
  if (videoRef.value) {
    currentVideoTime.value = videoRef.value.currentTime
    if (syncPlay.value && currentTime.value !== videoRef.value.currentTime) currentTime.value = videoRef.value.currentTime
    if (videoRef.value.currentTime >= (clipStartTime.value + internalDuration.value)) { videoRef.value.pause(); isVideoPlaying.value = false }
  }
}

const handleVideoEnded = () => { isVideoPlaying.value = false }
const onClipStartTimeChange = (event: Event) => { clipStartTime.value = parseFloat((event.target as HTMLInputElement).value) }

const startTimePercent = computed(() => videoDuration.value === 0 ? 0 : ((clipStartTime.value || 0) / videoDuration.value) * 100)
const durationPercent = computed(() => videoDuration.value === 0 ? 0 : (internalDuration.value / videoDuration.value) * 100)

const handlePreviewTimeUpdate = () => {
  if (isIntervalPlaying.value && croppingPreviewRef.value) {
    const endTime = clipStartTime.value + internalDuration.value
    if (croppingPreviewRef.value.currentTime >= endTime) croppingPreviewRef.value.currentTime = clipStartTime.value
  }
}

const updateIntervalPosition = () => {
  if (intervalFrameId) cancelAnimationFrame(intervalFrameId)
  const checkEnd = () => {
    if (!isIntervalPlaying.value || !croppingPreviewRef.value) return
    const endTime = clipStartTime.value + internalDuration.value
    if (croppingPreviewRef.value.currentTime >= endTime) croppingPreviewRef.value.currentTime = clipStartTime.value
    intervalFrameId = requestAnimationFrame(checkEnd)
  }
  intervalFrameId = requestAnimationFrame(checkEnd)
}

const startIntervalPreview = () => {
  if (!croppingPreviewRef.value) return
  if (isIntervalPlaying.value) { stopIntervalPreview(); return }
  isIntervalPlaying.value = true
  croppingPreviewRef.value.currentTime = clipStartTime.value
  croppingPreviewRef.value.play()
  updateIntervalPosition()
}

const stopIntervalPreview = () => {
  if (croppingPreviewRef.value) croppingPreviewRef.value.pause()
  isIntervalPlaying.value = false
  if (intervalFrameId) { cancelAnimationFrame(intervalFrameId); intervalFrameId = null }
}

const resetInterval = () => {
  if (croppingPreviewRef.value) { croppingPreviewRef.value.currentTime = clipStartTime.value; croppingPreviewRef.value.pause(); isIntervalPlaying.value = false }
  if (intervalFrameId) { cancelAnimationFrame(intervalFrameId); intervalFrameId = null }
}

const seekVideo = (event: MouseEvent) => {
  if (!croppingPreviewRef.value || !isCroppingMode.value) return
  const video = event.currentTarget as HTMLVideoElement
  const rect = video.getBoundingClientRect()
  const percent = (event.clientX - rect.left) / rect.width
  const time = percent * videoDuration.value
  const endTime = clipStartTime.value + internalDuration.value
  if (time >= clipStartTime.value && time <= endTime) video.currentTime = time
}

const seekByClick = (event: MouseEvent) => {
  if (!croppingPreviewRef.value) return
  const track = event.currentTarget as HTMLElement
  const rect = track.getBoundingClientRect()
  const percent = (event.clientX - rect.left) / rect.width
  const time = percent * videoDuration.value
  const endTime = clipStartTime.value + internalDuration.value
  if (time >= clipStartTime.value && time <= endTime) croppingPreviewRef.value.currentTime = time
}

const cancelCrop = () => { stopIntervalPreview(); isCroppingMode.value = false }

const clearVideo = () => {
  stopIntervalPreview()
  isCroppingMode.value = false
  if (videoInputRef.value) videoInputRef.value.value = ''
  videoUrl.value = null
  videoDuration.value = 0
  clipStartTime.value = 0
  currentVideoTime.value = 0
  isVideoPlaying.value = false
}

const toggleVideoPlay = () => {
  if (!videoRef.value) return
  if (isVideoPlaying.value) { videoRef.value.pause(); isVideoPlaying.value = false }
  else {
    if (videoRef.value.currentTime >= (clipStartTime.value + internalDuration.value)) videoRef.value.currentTime = clipStartTime.value
    videoRef.value.play()
    isVideoPlaying.value = true
  }
}

const resetVideo = () => {
  if (videoRef.value) { videoRef.value.currentTime = clipStartTime.value; currentVideoTime.value = clipStartTime.value; videoRef.value.pause(); isVideoPlaying.value = false }
}

const loadFFmpeg = async () => { if (ffmpegLoaded.value) return; await ffmpeg.load({ coreURL: 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm/ffmpeg-core.js' }); ffmpegLoaded.value = true }

const cropAndUpload = async () => {
  if (!videoUrl.value) return
  isProcessing.value = true
  try {
    await loadFFmpeg()
    stopIntervalPreview()
    const response = await fetch(videoUrl.value)
    const blob = await response.blob()
    const arrayBuffer = await blob.arrayBuffer()
    const uint8Array = new Uint8Array(arrayBuffer)
    await ffmpeg.writeFile('input.mp4', uint8Array)
    const duration = internalDuration.value
    await ffmpeg.exec(['-i', 'input.mp4', '-ss', clipStartTime.value.toString(), '-t', duration.toString(), '-c:v', 'libx264', '-c:a', 'aac', '-movflags', '+faststart', 'output.mp4'])
    const outputData = await ffmpeg.readFile('output.mp4') as Uint8Array
    const outputBlob = new Blob([outputData], { type: 'video/mp4' })
    const formData = new FormData()
    formData.append('video', outputBlob, 'cropped_video.mp4')
    const res = await fetch('/api/videos/upload/', { method: 'POST', body: formData })
    if (!res.ok) throw new Error('Upload failed')
    const result = await res.json()
    console.log('上传成功:', result)
    isCroppingMode.value = false
    videoUrl.value = result.url
    videoDuration.value = result.duration
    clipStartTime.value = 0
    currentVideoTime.value = 0
    await ffmpeg.deleteFile('input.mp4')
    await ffmpeg.deleteFile('output.mp4')
  } catch (error) {
    console.error('视频裁剪失败:', error)
    alert('视频裁剪失败：' + (error as Error).message)
  } finally { isProcessing.value = false }
}

watch(internalDuration, (newDuration) => {
  if (videoUrl.value) {
    const maxStartTime = Math.max(0, videoDuration.value - newDuration)
    if (clipStartTime.value > maxStartTime) clipStartTime.value = maxStartTime
  }
})

watch(currentTime, (newTime) => {
  if (syncPlay.value && isDraggingMaster.value && videoRef.value && !isCroppingMode.value) videoRef.value.currentTime = newTime
})

onUnmounted(() => {
  if (intervalFrameId) cancelAnimationFrame(intervalFrameId)
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
})
</script>

<style scoped>
.rotation-edit { background: var(--bg-tertiary); border-radius: 16px; padding: 20px; user-select: none; -webkit-user-select: none; }
.rotation-edit * { user-select: none; -webkit-user-select: none; }
.rotation-edit input, .rotation-edit select, .rotation-edit textarea { user-select: text; -webkit-user-select: text; }
.edit-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.char-tabs { display: flex; gap: 8px; align-items: center; }
.tab-label { color: var(--text-secondary); font-size: 14px; font-weight: 500; }
.char-tab { display: flex; align-items: center; gap: 6px; padding: 8px 12px; background: var(--bg-primary); border: 2px solid transparent; border-radius: 10px; cursor: pointer; transition: all 0.2s; }
.char-tab.active { background: var(--accent-color); color: white; }
.char-tab img { width: 28px; height: 28px; border-radius: 6px; }
.header-controls { display: flex; align-items: center; gap: 16px; }
.duration-input { display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 14px; }
.btn-save { padding: 8px 20px; background: var(--accent-color); color: white; border: none; border-radius: 10px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.btn-save:hover { opacity: 0.9; transform: scale(1.02); }
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; padding-left: 58px; }
.tool-btn { padding: 8px 16px; background: var(--bg-primary); border: none; border-radius: 10px; cursor: pointer; transition: all 0.2s; font-size: 14px; }
.tool-btn.active { background: var(--accent-color); color: white; }
.current-time { margin-left: auto; color: var(--text-secondary); font-size: 14px; display: flex; align-items: center; gap: 12px; }
.btn-reset { padding: 4px 10px; background: var(--bg-tertiary); border: none; border-radius: 6px; cursor: pointer; font-size: 12px; color: var(--text-secondary); }
.btn-clear { padding: 4px 10px; background: rgba(255, 59, 48, 0.15); border: none; border-radius: 6px; cursor: pointer; font-size: 12px; color: #ff3b30; transition: all 0.2s; }
.btn-clear:hover { background: rgba(255, 59, 48, 0.25); }
.timeline { position: relative; padding-top: 8px; }
.master-timeline-row { display: flex; align-items: center; height: 48px; margin-bottom: 8px; }
.master-label { width: 48px; flex-shrink: 0; background: transparent; border-radius: 8px; margin-right: 10px; }
.master-timeline { position: relative; flex: 1; height: 40px; background: var(--bg-primary); border-radius: 8px; cursor: grab; user-select: none; transition: all 0.2s; border: 2px solid transparent; z-index: 10; }
.master-timeline:hover { background: rgba(255, 255, 255, 0.08); }
.master-timeline.dragging { cursor: grabbing; border-color: var(--accent-color); background: rgba(255, 255, 255, 0.12); box-shadow: 0 0 20px rgba(255, 255, 255, 0.1); }
.master-scale-label { position: absolute; bottom: 4px; font-size: 11px; font-weight: 500; color: rgba(255, 255, 255, 0.6); font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif; transform: translateX(-50%); pointer-events: none; }
.playhead-overlay { position: absolute; top: 0; bottom: 0; left: 58px; pointer-events: none; z-index: 200; }
.playhead-indicator { position: absolute; top: 22px; bottom: 0; width: 2px; transform: translateX(-50%); pointer-events: none; transition: width 0.15s; }
.playhead-indicator.dragging { width: 3px; }
.snap-indicator { position: absolute; top: 22px; bottom: 0; pointer-events: none; z-index: 150; }
.snap-line { position: absolute; top: 0; bottom: 0; left: 50%; width: 1px; transform: translateX(-50%); background: rgba(0, 212, 255, 0.4); box-shadow: 0 0 4px rgba(0, 212, 255, 0.2); border-radius: 1px; }
.mouse-snap-indicator { position: absolute; top: 0; bottom: 0; pointer-events: none; z-index: 100; }
.mouse-snap-line { position: absolute; top: 0; bottom: 0; left: 50%; width: 2px; transform: translateX(-50%); background: rgba(0, 212, 255, 0.6); box-shadow: 0 0 6px rgba(0, 212, 255, 0.4); border-left: 1px dashed rgba(0, 212, 255, 0.8); border-right: 1px dashed rgba(0, 212, 255, 0.8); }
.playhead-arrow { position: absolute; top: -8px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-top: 8px solid rgba(255, 255, 255, 0.9); transition: all 0.15s; filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3)); }
.playhead-line { position: absolute; top: 0; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; background: rgba(255, 255, 255, 0.6); transition: all 0.15s; }
.playhead-indicator.dragging .playhead-arrow { border-top-color: var(--accent-color); filter: drop-shadow(0 0 6px var(--accent-color)); }
.playhead-indicator.dragging .playhead-line { background: var(--accent-color); box-shadow: 0 0 15px var(--accent-color); }
.char-row { display: flex; align-items: center; height: 48px; margin-bottom: 24px; cursor: pointer; position: relative; }
.char-row:last-child { margin-bottom: 0; }
.char-row.active .row-label { background: var(--accent-color); }
.row-label { width: 48px; flex-shrink: 0; background: var(--bg-primary); border-radius: 8px; margin-right: 10px; display: flex; align-items: center; justify-content: center; padding: 4px; transition: all 0.2s; }
.row-label img { width: 36px; height: 36px; border-radius: 8px; }
.row-timeline { position: relative; flex: 1; height: 36px; background: var(--bg-primary); border-radius: 8px; overflow: visible; transition: all 0.2s; border: 2px solid transparent; }
.char-row.can-interact:hover .row-timeline.interacting { background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.2); cursor: pointer; }
.char-row.can-interact .row-timeline.selecting { background: rgba(255, 255, 255, 0.12); border-color: var(--accent-color); box-shadow: 0 0 15px rgba(255, 255, 255, 0.1); }
.char-tab.disabled { opacity: 0.4; cursor: not-allowed; }
.row-selection-overlay { position: absolute; top: 0; bottom: 0; background: var(--accent-color); opacity: 0.3; border-radius: 6px; pointer-events: none; z-index: 1; }
.segments-container { position: absolute; top: 4px; left: 0; right: 0; bottom: 4px; z-index: 2; overflow: visible; }
.segment-block { position: absolute; top: 50%; transform: translateY(-50%); height: 26px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 500; font-size: 9px; white-space: nowrap; background: #636366; z-index: 1; border-right: 1px solid rgba(255, 255, 255, 0.3); box-sizing: border-box; }
.segment-block.completed { background: #34c759; }
.segment-block.switch { background: #ff7f16; }
.segment-block.is-variation { background: #ff9500; opacity: 0.7; }
.segment-label { font-family: -apple-system, BlinkMacSystemFont, sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; padding: 0 4px; }
.switch-arrow-container { position: absolute; top: 100%; left: 0; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; z-index: 1000; pointer-events: none; }
.switch-arrow-container.arrow-up { top: auto; bottom: 100%; flex-direction: column-reverse; }
.switch-arrow-line { width: 2px; background: #ff7f16; height: var(--arrow-height, 16px); flex-shrink: 0; }
.switch-arrow-head { width: 12px; height: 12px; flex-shrink: 0; }
.switch-arrow-container.arrow-up .switch-arrow-head { transform: rotate(180deg); }
.switch-arrow-label { font-size: 11px; color: #ff7f16; font-family: -apple-system, BlinkMacSystemFont, sans-serif; white-space: nowrap; font-weight: 500; position: absolute; left: 14px; bottom: 0px; }
.dialog-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; align-items: center; justify-content: center; z-index: 9999; }
.dialog { background: var(--bg-secondary); border-radius: 16px; padding: 24px; width: 90%; max-width: 450px; color: var(--text-primary); box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5); border: 1px solid var(--border-color); }
.dialog h3 { margin: 0 0 16px 0; font-size: 18px; font-weight: 600; }
.dialog-content { margin-bottom: 20px; }
.time-range { background: var(--bg-primary); padding: 12px; border-radius: 8px; margin-bottom: 16px; font-size: 14px; color: var(--text-secondary); }
.preset-buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.preset-btn { padding: 8px 16px; background: var(--bg-tertiary); border: none; border-radius: 8px; cursor: pointer; font-weight: 500; transition: all 0.2s; }
.preset-btn:hover { background: var(--accent-color); color: white; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 14px; color: var(--text-secondary); }
.form-input { width: 100%; padding: 10px 12px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-primary); font-size: 14px; }
.form-input:focus { outline: none; border-color: var(--accent-color); }
.target-characters { display: flex; flex-direction: column; gap: 8px; }
.target-char-btn { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-primary); border: 2px solid transparent; border-radius: 10px; cursor: pointer; transition: all 0.2s; }
.target-char-btn:hover { border-color: var(--accent-color); }
.target-char-btn.active { background: var(--accent-color); border-color: var(--accent-color); color: white; }
.target-char-btn img { width: 32px; height: 32px; border-radius: 6px; }
.warning-text { color: #ff3b30; font-size: 13px; margin-top: 12px; padding: 8px 12px; background: rgba(255, 59, 48, 0.1); border-radius: 6px; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 12px; }
.btn-cancel { padding: 10px 20px; background: var(--bg-tertiary); border: none; border-radius: 8px; cursor: pointer; font-weight: 500; transition: all 0.2s; }
.btn-cancel:hover { background: #3a3a3c; }
.btn-confirm { padding: 10px 20px; background: var(--accent-color); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500; transition: all 0.2s; }
.btn-confirm:hover { opacity: 0.9; transform: scale(1.02); }

/* 视频上传区域 */
.video-section { margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--border-color); }
.video-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.video-header h3 { margin: 0; font-size: 16px; font-weight: 600; color: var(--text-primary); }
.btn-clear-video { padding: 6px 12px; background: rgba(255, 59, 48, 0.15); border: none; border-radius: 6px; cursor: pointer; font-size: 12px; color: #ff3b30; transition: all 0.2s; }
.btn-clear-video:hover { background: rgba(255, 59, 48, 0.25); }
.video-upload { padding: 40px; background: var(--bg-primary); border: 2px dashed var(--border-color); border-radius: 12px; cursor: pointer; transition: all 0.2s; text-align: center; }
.video-upload:hover { border-color: var(--accent-color); background: rgba(255, 45, 85, 0.05); }
.video-input { display: none; }
.upload-hint { display: flex; flex-direction: column; align-items: center; gap: 8px; color: var(--text-secondary); }
.upload-icon { font-size: 32px; }
.video-preview { display: flex; flex-direction: column; gap: 12px; }
.video-player { width: 100%; max-height: 400px; background: #000; border-radius: 12px; object-fit: contain; }
.video-controls { display: flex; flex-direction: column; gap: 12px; padding: 16px; background: var(--bg-primary); border-radius: 12px; }
.video-buttons { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.sync-play { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--text-secondary); cursor: pointer; user-select: none; }
.sync-play input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; }
.btn-video-play, .btn-video-reset { padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.btn-video-play { background: #34c759; color: white; }
.btn-video-play:hover { background: #30d158; }
.btn-video-reset { background: var(--bg-tertiary); color: var(--text-primary); }
.btn-video-reset:hover { background: #3a3a3c; }
.video-progress { font-size: 13px; color: var(--text-secondary); text-align: right; }

/* 全屏裁剪弹窗 */
.cropping-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.9); display: flex; align-items: center; justify-content: center; z-index: 9999; }
.cropping-panel { background: #1c1c1e; border-radius: 16px; padding: 24px; width: 90%; max-width: 800px; max-height: 90vh; overflow-y: auto; border: 1px solid #3a3a3c; }
.cropping-title { margin-bottom: 20px; text-align: center; }
.cropping-title h4 { margin: 0 0 8px 0; font-size: 20px; font-weight: 600; color: white; }
.cropping-hint { margin: 0; font-size: 14px; color: #8e8e93; }
.cropping-area { display: flex; flex-direction: column; gap: 20px; }
.video-preview-wrapper { width: 100%; background: #000; border-radius: 12px; overflow: hidden; }
.cropping-video { width: 100%; max-height: 400px; object-fit: contain; cursor: pointer; }
.progress-container { position: relative; height: 120px; padding: 0 8px; }
.progress-track { position: absolute; top: 20px; left: 0; right: 0; height: 8px; background: #3a3a3c; border-radius: 4px; overflow: hidden; cursor: pointer; }
.progress-highlight { position: absolute; top: 0; height: 100%; background: rgba(255, 45, 85, 0.6); border-radius: 4px; pointer-events: none; }
.progress-slider { -webkit-appearance: none; appearance: none; position: absolute; top: 16px; left: 0; right: 0; height: 16px; background: transparent; z-index: 50; cursor: grab; margin: 0; }
.progress-slider::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; background: #ff2d55; border-radius: 50%; cursor: grab; box-shadow: 0 2px 8px rgba(255, 45, 85, 0.5); transition: all 0.2s; }
.progress-slider::-webkit-slider-thumb:hover { transform: scale(1.2); box-shadow: 0 4px 12px rgba(255, 45, 85, 0.7); }
.progress-slider::-moz-range-thumb { width: 20px; height: 20px; background: #ff2d55; border-radius: 50%; cursor: grab; box-shadow: 0 2px 8px rgba(255, 45, 85, 0.5); border: none; transition: all 0.2s; }
.progress-slider::-moz-range-thumb:hover { transform: scale(1.2); box-shadow: 0 4px 12px rgba(255, 45, 85, 0.7); }
.time-labels { position: absolute; top: 48px; left: 0; right: 0; display: flex; justify-content: space-between; }
.time-label { position: absolute; transform: translateX(-50%); font-size: 12px; color: #8e8e93; white-space: nowrap; }
.time-label.start-label { left: 0; }
.time-label.end-label { right: 0; transform: translateX(50%); }
.interval-playback-bar { position: absolute; top: 70px; height: 36px; background: rgba(0, 0, 0, 0.8); border: 1px solid #ff2d55; border-radius: 6px; display: flex; align-items: center; justify-content: center; z-index: 100; pointer-events: auto; transition: all 0.3s; }
.playback-controls { display: flex; gap: 8px; align-items: center; }
.control-btn { width: 32px; height: 32px; background: rgba(255, 255, 255, 0.1); border: none; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; transition: all 0.2s; }
.control-btn:hover { background: #ff2d55; transform: scale(1.1); }
.control-btn:active { transform: scale(0.95); }
.cropping-buttons { display: flex; justify-content: center; gap: 12px; margin-top: 12px; }
.btn-cancel-crop { padding: 12px 24px; background: rgba(255, 59, 48, 0.15); border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; color: #ff3b30; transition: all 0.2s; }
.btn-cancel-crop:hover { background: rgba(255, 59, 48, 0.25); }
.btn-confirm-crop { padding: 12px 24px; background: #ff2d55; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; color: white; transition: all 0.2s; }
.btn-confirm-crop:hover:not(:disabled) { opacity: 0.9; transform: scale(1.02); }
.btn-confirm-crop:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
