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
        <div class="duration-input-wrapper">
          <button @click="showHelpTip = true" class="help-icon-btn" title="查看注意事项">
            <img src="/assets/info-fill.svg" alt="帮助" class="help-icon" />
          </button>
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
        </div>
        <button @click="$emit('cancel')" class="btn-cancel" style="margin-right: 8px;">取消</button>
        <button @click="$emit('save', getRotationData())" class="btn-save">保存</button>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <button v-if="characters.length > 1" class="tool-btn" @click="addSwitch">🔄 切人</button>
      <button v-if="characters.length > 1" class="tool-btn" @click="addVariation">🎵 变奏</button>
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
        <div class="row-timeline" :class="{ 'selecting': isSelecting && activeCharIndex === charIndex }">
          <div class="time-grid">
            <div v-for="s in Math.ceil(internalDuration)" :key="'row-grid-' + char + '-' + s" class="grid-line" :style="{ left: getTimePercent(s - 1) + '%' }"></div>
          </div>
          <div v-if="isSelecting && activeCharIndex === charIndex && selection" class="row-selection-overlay" :style="{ left: getTimePercent(selection.start) + '%', width: getTimePercent(selection.end - selection.start) + '%' }"></div>
          <div class="segments-container">
            <template v-for="(segment, segIndex) in getMergedSegmentsWithVariation(char, getSegments(char))">
              <div v-if="segment.type !== 'switch' || segment.isVariationSeg" :key="'seg-' + segIndex" :class="['segment-block', segment.type, { completed: segment.startTime <= currentTime, 'is-variation': segment.isVariationSeg }]" :style="{ left: getTimePercent(segment.startTime) + '%', width: getTimePercent(segment.endTime - segment.startTime) + '%' }" @mouseenter="onSegmentMouseEnter(char, segIndex, segment)" @mousemove="onSegmentMouseMove($event, char, segIndex, segment)" @mouseleave="onSegmentMouseLeave">
                <span class="segment-label">{{ segment.display }}</span>
                <div v-if="hoveredSegment?.char === char && hoveredSegment?.segIndex === segIndex && hoveredSegment?.edge === 'left'" class="segment-edge-highlight left"></div>
                <div v-if="hoveredSegment?.char === char && hoveredSegment?.segIndex === segIndex && hoveredSegment?.edge === 'right'" class="segment-edge-highlight right"></div>
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
      <!-- 帮助提示弹窗 -->
      <div v-if="showHelpTip" class="dialog-overlay" @click.self="showHelpTip = false">
        <div class="dialog help-dialog">
          <div class="dialog-header">
            <h3>⚠️ 添加轴注意事项</h3>
            <button @click="showHelpTip = false" class="dialog-close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="dialog-content help-content">
            <div class="help-section">
              <h4>📌 基本流程</h4>
              <ol>
                <li><strong>选择首发角色</strong> - 点击顶部角色标签切换当前编辑角色</li>
                <li><strong>设置总时长</strong> - 在右上角输入轴总时长（秒）</li>
                <li><strong>添加操作</strong> - 在角色时间轴上拖拽选择时间范围，弹出对话框选择技能</li>
                <li><strong>添加切人</strong> - 点击"🔄 切人"按钮选择目标角色</li>
                <li><strong>添加变奏</strong> - 点击"🎵 变奏"按钮设置变奏时长</li>
                <li><strong>上传视频</strong> - 可选，视频时长需≥轴总时长</li>
              </ol>
            </div>
            <div class="help-section">
              <h4>⚠️ 重要提示</h4>
              <ul>
                <li><strong>首发角色限制：</strong>添加任何操作后不能切换首发角色，需清空后才能重新选择</li>
                <li><strong>切人 CD：</strong>两次切人间隔必须≥1 秒，否则显示红色警告</li>
                <li><strong>视频时长：</strong>上传视频时长必须≥轴总时长</li>
                <li><strong>时间吸附：</strong>拖拽时自动吸附到操作块边缘（阈值 0.15s）</li>
              </ul>
            </div>
            <div class="help-section">
              <h4>🎮 快捷操作</h4>
              <ul>
                <li><strong>拖拽播放头：</strong>在顶部时间轴拖拽切换当前时间</li>
                <li><strong>调整操作块：</strong>鼠标悬停操作块边缘可调整起止时间</li>
                <li><strong>重置：</strong>点击"↺ 重置"播放头归零</li>
                <li><strong>清空：</strong>点击"🗑 清空"清除所有操作</li>
              </ul>
            </div>
          </div>
          <div class="dialog-actions">
            <button @click="showHelpTip = false" class="btn-confirm">知道了</button>
          </div>
        </div>
      </div>

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


    </Teleport>

    <!-- 参考视频区域 -->
    <div class="video-section">
      <div class="video-header">
      <div class="video-header-left">
        <h3>参考视频</h3>
        <span v-if="videoUrl && !isCroppingMode" class="sync-checkbox">
          <label class="checkbox-label">
            <input type="checkbox" v-model="isSyncPlaying" class="checkbox-input" />
            同步播放
          </label>
        </span>
      </div>
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
      <video ref="videoRef" :src="videoUrl" class="video-player" controls @loadedmetadata="handleVideoLoaded" @timeupdate="handleVideoTimeUpdate" @play="handleVideoPlay" @pause="handleVideoPause" @seeked="handleVideoSeeked" @ended="handleVideoEnded"></video>
    </div>

    <!-- 裁剪模式弹窗 - 紧凑 Apple 风格 -->
    <Teleport to="body">
      <div v-if="isCroppingMode" class="crop-overlay" @click.self="cancelCrop">
        <div class="crop-panel">
          <div class="crop-header">
            <span class="crop-title">裁剪视频</span>
            <button @click="cancelCrop" class="crop-close">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          
          <div class="crop-video-wrap">
            <video ref="croppingPreviewRef" :src="videoUrl" class="crop-video" @timeupdate="handlePreviewTimeUpdate"></video>
            <div class="crop-play-btn" @click="toggleCroppingPlay">
              <svg v-if="!isCroppingVideoPlaying" width="20" height="20" viewBox="0 0 20 20" fill="white">
                <path d="M6 4L16 10L6 16V4Z"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="white">
                <rect x="5" y="4" width="3" height="12" rx="1"/>
                <rect x="12" y="4" width="3" height="12" rx="1"/>
              </svg>
            </div>
          </div>
          
          <div class="crop-timeline">
            <div class="crop-timeline-wrap">
              <div class="crop-timeline-bar" @mousedown="startDragClip" @touchstart="startDragClip">
                <div class="crop-timeline-left"></div>
                <div class="crop-timeline-range" :style="{ left: highlightLeft + '%', width: highlightWidth + '%' }">
                  <div class="crop-timeline-fill"></div>
                </div>
              </div>
            </div>
            <div class="crop-time-info">
              <span class="crop-time-start">{{ clipStartTime.toFixed(1) }}s</span>
              <span class="crop-time-duration">片段 {{ internalDuration }}s</span>
              <span class="crop-time-end">{{ (clipStartTime + internalDuration).toFixed(1) }}s</span>
            </div>
          </div>
          
          <div class="crop-actions">
            <button @click="cancelCrop" class="crop-btn crop-btn-cancel" :disabled="isProcessing">取消</button>
            <button @click="cropAndUpload" :disabled="isProcessing" class="crop-btn crop-btn-confirm">
              确认裁剪
            </button>
          </div>
        </div>
      </div>
      
      <!-- 全屏 Loading -->
      <div v-if="isProcessing" class="loading-mask">
        <div class="loading-spinner">
          <svg width="40" height="40" viewBox="0 0 40 40">
            <circle cx="20" cy="20" r="16" stroke="rgba(255,255,255,0.2)" stroke-width="3" fill="none"/>
            <path d="M36 20A16 16 0 0 0 4 20" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
          </svg>
          <span class="loading-text">视频处理中...</span>
        </div>
      </div>
      
      <!-- Toast 提示 -->
      <Teleport to="body">
        <div v-if="toastVisible" :class="['toast', toastType]">
          {{ toastMessage }}
        </div>
      </Teleport>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'

interface Segment { type: 'action' | 'switch'; startTime: number; endTime?: number; display: string; description?: string; target?: string }
interface ActionFormData { display: string; description: string }
interface VariationFormData { target: string; duration: number }
interface MergedSegment { startTime: number; endTime: number; display: string; description: string; count: number; type?: 'action' | 'switch'; isVariationSeg?: boolean }

const props = defineProps<{ 
  characters: string[]
  totalDuration?: number
  initialVideoUrl?: string | null
  initialSegments?: { [key: string]: Segment[] }
}>()
const emit = defineEmits<{ save: [data: any]; cancel: [] }>()

const internalDuration = ref(props.totalDuration || 30)
const firstCharIndex = ref(0)
const activeCharIndex = ref(0)
const currentTime = ref(0)
const segmentsData = ref<{ [key: string]: Segment[] }>({})

// 初始化视频 URL
const videoUrl = ref<string | null>(props.initialVideoUrl || null)

// 初始化时间轴数据
if (props.initialSegments) {
  segmentsData.value = JSON.parse(JSON.stringify(props.initialSegments))
}

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
const videoRef = ref<HTMLVideoElement | null>(null)
const videoInputRef = ref<HTMLInputElement | null>(null)
const videoDuration = ref(0)
const clipStartTime = ref(0)
const isProcessing = ref(false)
const isCroppingMode = ref(false)
const isSyncPlaying = ref(false)
const isVideoPlaying = ref(false)
const isTimelinePlaying = ref(false)
let timelinePlayInterval: number | null = null
let videoSyncFrame: number | null = null
let blobUrlToRevoke: string | null = null
let syncAnimationFrame: number | null = null
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')

const showToast = (message: string, type: 'success' | 'error' = 'success') => {
  toastMessage.value = message
  toastType.value = type
  toastVisible.value = true
  setTimeout(() => { toastVisible.value = false }, 3000)
}

const isIntervalPlaying = ref(false)
const isCroppingVideoPlaying = ref(false)
let intervalFrameId: number | null = null
const croppingPreviewRef = ref<HTMLVideoElement | null>(null)
const ffmpeg = ref<any>(null)
const ffmpegLoaded = ref(false)

const snapThreshold = 0.2
const isSnapping = ref(false)
const snapPoint = ref(0)
const isMouseSnapping = ref(false)
const mouseSnapPoint = ref(0)
const hoveredSegment = ref<{ char: string; segIndex: number; edge: 'left' | 'right' | null } | null>(null)

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
  if (!currentChar) return points
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
const showHelpTip = ref(false)

const setFirstCharacter = (index: number) => { if (!hasAnyOperations.value) firstCharIndex.value = index }
const addSwitch = () => { clickTime.value = currentTime.value; showSwitchDialog.value = true; switchWarning.value = '' }
const addVariation = () => { clickTime.value = currentTime.value; variationForm.value.target = getOtherCharacters()[0] || ''; variationForm.value.duration = 1; showVariationDialog.value = true }
const reset = () => { 
  currentTime.value = 0
  stopTimelinePlay()
  if (isSyncPlaying.value && videoRef.value) {
    videoRef.value.currentTime = 0
  }
}

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
  
  // 同步播放模式下，拖拽时实时同步视频
  if (isSyncPlaying.value && videoRef.value) {
    videoRef.value.currentTime = currentTime.value
  }
  
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
  // 拖拽结束后同步视频进度
  if (isSyncPlaying.value && videoRef.value) {
    videoRef.value.currentTime = currentTime.value
  }
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
  if (selection.value && selection.value.end - selection.value.start > 0.1) { 
    isSelecting.value = false
    showActionDialog.value = true; actionForm.value = { display: '', description: '' } 
  }
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

const edgeSnapThreshold = 0.15

const onSegmentMouseEnter = (char: string, segIndex: number, segment: any) => {
  hoveredSegment.value = { char, segIndex, edge: null }
}

const onSegmentMouseMove = (event: MouseEvent, char: string, segIndex: number, segment: any) => {
  const edgeThresholdSec = 0.5
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const percent = (event.clientX - rect.left) / rect.width
  const time = segment.startTime + percent * (segment.endTime - segment.startTime)
  
  const distToStart = Math.abs(time - segment.startTime)
  const distToEnd = segment.endTime ? Math.abs(time - segment.endTime) : Infinity
  
  if (distToStart < edgeThresholdSec) {
    hoveredSegment.value = { char, segIndex, edge: 'left' }
    mouseSnapPoint.value = segment.startTime
    isMouseSnapping.value = true
  } else if (distToEnd < edgeThresholdSec) {
    hoveredSegment.value = { char, segIndex, edge: 'right' }
    mouseSnapPoint.value = segment.endTime
    isMouseSnapping.value = true
  } else {
    hoveredSegment.value = { char, segIndex, edge: null }
    isMouseSnapping.value = false
  }
}

const onSegmentMouseLeave = () => {
  hoveredSegment.value = null
  isMouseSnapping.value = false
}

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
  // 切人 CD 时间：1 秒
  if (lastTime !== null && clickTime.value - lastTime < 1) {
    switchWarning.value = `切人 CD 中，请等待 ${(1 - (clickTime.value - lastTime)).toFixed(1)}s`
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

const getRotationData = () => ({ 
  name: '自定义输出轴', 
  totalDuration: internalDuration.value, 
  characters: props.characters.map(char => ({ name: char, segments: segmentsData.value[char] })),
  videoUrl: videoUrl.value
})

// 视频相关函数
const triggerVideoUpload = () => { videoInputRef.value?.click() }

const handleVideoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  
  // 检查文件大小 - 500MB 限制
  const maxSize = 500 * 1024 * 1024
  const fileSizeMB = (file.size / 1024 / 1024).toFixed(1)
  if (file.size > maxSize) {
    showToast(`视频文件过大 (${fileSizeMB}MB)，最大支持 500MB`, 'error')
    target.value = ''
    return
  }
  
  // 释放旧的 blob URL
  if (blobUrlToRevoke) {
    URL.revokeObjectURL(blobUrlToRevoke)
    blobUrlToRevoke = null
  }
  
  const url = URL.createObjectURL(file)
  blobUrlToRevoke = url
  videoUrl.value = url
  
  const tempVideo = document.createElement('video')
  tempVideo.src = url
  await new Promise<void>((resolve) => {
    tempVideo.onloadedmetadata = () => {
      videoDuration.value = tempVideo.duration
      if (videoDuration.value < internalDuration.value) {
        showToast(`视频时长不足，需大于 ${internalDuration.value}s`, 'error')
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

const handleVideoLoaded = () => { 
  if (videoRef.value) { 
    videoDuration.value = videoRef.value.duration
    clipStartTime.value = 0
  } 
}

const handleVideoTimeUpdate = () => {
  if (videoRef.value && isSyncPlaying.value) {
    currentTime.value = videoRef.value.currentTime
  }
}

const handleVideoPlay = () => {
  isVideoPlaying.value = true
  if (isSyncPlaying.value) {
    startSyncLoop()
  }
}

const handleVideoPause = () => {
  isVideoPlaying.value = false
  if (isSyncPlaying.value) {
    stopSyncLoop()
  }
}

const handleVideoEnded = () => {
  isVideoPlaying.value = false
  isTimelinePlaying.value = false
  currentTime.value = 0
  if (syncAnimationFrame) {
    cancelAnimationFrame(syncAnimationFrame)
    syncAnimationFrame = null
  }
  if (timelinePlayInterval) {
    clearTimeout(timelinePlayInterval)
    timelinePlayInterval = null
  }
}

const handleVideoSeeked = () => {
  if (videoRef.value && isSyncPlaying.value) {
    currentTime.value = videoRef.value.currentTime
  }
}

let lastSyncTime = 0

const startSyncLoop = () => {
  if (syncAnimationFrame) return
  
  const sync = () => {
    if (!videoRef.value || !isVideoPlaying.value) {
      syncAnimationFrame = null
      return
    }
    
    const videoTime = videoRef.value.currentTime
    if (Math.abs(videoTime - currentTime.value) > 0.3) {
      currentTime.value = videoTime
    }
    
    if (currentTime.value >= internalDuration.value) {
      currentTime.value = 0
      stopTimelinePlay()
      syncAnimationFrame = null
      return
    }
    
    lastSyncTime = videoTime
    syncAnimationFrame = requestAnimationFrame(sync)
  }
  
  sync()
}

const syncTimelineToVideo = () => {
  if (!videoRef.value || !isSyncPlaying.value || !isTimelinePlaying.value) return
  
  const timeDiff = Math.abs(currentTime.value - videoRef.value.currentTime)
  if (timeDiff > 0.3) {
    videoRef.value.currentTime = currentTime.value
  }
  
  if (currentTime.value >= internalDuration.value) {
    stopTimelinePlay()
    currentTime.value = 0
    return
  }
  
  videoSyncFrame = requestAnimationFrame(syncTimelineToVideo)
}

const stopSyncLoop = () => {
  if (syncAnimationFrame) {
    cancelAnimationFrame(syncAnimationFrame)
    syncAnimationFrame = null
  }
}

const syncVideoToTimeline = () => {
  if (!videoRef.value || !isSyncPlaying.value) return
  
  const timeDiff = Math.abs(videoRef.value.currentTime - currentTime.value)
  if (timeDiff > 0.5) {
    videoRef.value.currentTime = currentTime.value
  }
}

const toggleTimelinePlay = () => {
  if (isTimelinePlaying.value) {
    stopTimelinePlay()
  } else {
    startTimelinePlay()
  }
}

const startTimelinePlay = () => {
  if (isTimelinePlaying.value) return
  isTimelinePlaying.value = true
  
  if (isSyncPlaying.value && videoRef.value) {
    videoRef.value.play().catch(() => {})
    syncTimelineToVideo()
  }
  
  const playLoop = () => {
    if (!isTimelinePlaying.value) return
    
    currentTime.value += 0.1
    
    if (currentTime.value >= internalDuration.value) {
      currentTime.value = 0
      stopTimelinePlay()
      return
    }
    
    timelinePlayInterval = window.setTimeout(playLoop, 100)
  }
  
  playLoop()
}

const stopTimelinePlay = () => {
  isTimelinePlaying.value = false
  if (timelinePlayInterval) {
    clearTimeout(timelinePlayInterval)
    timelinePlayInterval = null
  }
  if (videoSyncFrame) {
    cancelAnimationFrame(videoSyncFrame)
    videoSyncFrame = null
  }
  if (isSyncPlaying.value && videoRef.value && !isVideoPlaying.value) {
    videoRef.value.pause()
  }
}

const handlePreviewTimeUpdate = () => {
  if (isIntervalPlaying.value && croppingPreviewRef.value) {
    if (croppingPreviewRef.value.currentTime >= (clipStartTime.value + internalDuration.value)) {
      croppingPreviewRef.value.currentTime = clipStartTime.value
    }
  }
}

const toggleCroppingPlay = () => {
  if (!croppingPreviewRef.value) return
  if (isCroppingVideoPlaying.value) {
    croppingPreviewRef.value.pause()
    isCroppingVideoPlaying.value = false
    stopIntervalPreview()
  } else {
    croppingPreviewRef.value.currentTime = 0
    croppingPreviewRef.value.play()
    isCroppingVideoPlaying.value = true
    startIntervalPreview()
  }
}

const resetCroppingVideo = () => {
  if (croppingPreviewRef.value) {
    croppingPreviewRef.value.currentTime = 0
    croppingPreviewRef.value.pause()
    isCroppingVideoPlaying.value = false
  }
  stopIntervalPreview()
}

const updateIntervalPosition = () => {
  if (intervalFrameId) cancelAnimationFrame(intervalFrameId)
  const checkEnd = () => {
    if (!isIntervalPlaying.value || !croppingPreviewRef.value) return
    if (croppingPreviewRef.value.currentTime >= (clipStartTime.value + internalDuration.value)) {
      croppingPreviewRef.value.currentTime = clipStartTime.value
    }
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
  if (croppingPreviewRef.value) { croppingPreviewRef.value.currentTime = 0; croppingPreviewRef.value.pause(); isIntervalPlaying.value = false }
  if (intervalFrameId) { cancelAnimationFrame(intervalFrameId); intervalFrameId = null }
}

const onClipStartTimeChange = () => {
  stopIntervalPreview()
  if (croppingPreviewRef.value) {
    croppingPreviewRef.value.currentTime = 0
  }
}

const highlightLeft = computed(() => videoDuration.value === 0 ? 0 : ((clipStartTime.value || 0) / videoDuration.value) * 100)
const highlightWidth = computed(() => videoDuration.value === 0 ? 0 : (internalDuration.value / videoDuration.value) * 100)

let timelineBarRef: HTMLElement | null = null
let isDraggingClip = false
let dragOffset = 0

const startDragClip = (e: MouseEvent | TouchEvent) => {
  e.preventDefault()
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  
  const barEl = (e.target as HTMLElement).closest('.crop-timeline-bar')
  if (!barEl) return
  
  timelineBarRef = barEl as HTMLElement
  const rect = timelineBarRef.getBoundingClientRect()
  
  const clickPercent = (clientX - rect.left) / rect.width
  const clickTime = clickPercent * videoDuration.value
  dragOffset = clipStartTime.value - clickTime
  
  isDraggingClip = true
  
  window.addEventListener('mousemove', onDragClip)
  window.addEventListener('mouseup', endDragClip)
  window.addEventListener('touchmove', onDragClip)
  window.addEventListener('touchend', endDragClip)
}

const onDragClip = (e: MouseEvent | TouchEvent) => {
  if (!isDraggingClip || !timelineBarRef) return
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const rect = timelineBarRef.getBoundingClientRect()
  const percent = (clientX - rect.left) / rect.width
  const rawTime = percent * videoDuration.value + dragOffset
  const newTime = Math.max(0, Math.min(rawTime, videoDuration.value - internalDuration.value))
  clipStartTime.value = Math.round(newTime * 10) / 10
}

const endDragClip = () => {
  isDraggingClip = false
  timelineBarRef = null
  window.removeEventListener('mousemove', onDragClip)
  window.removeEventListener('mouseup', endDragClip)
  window.removeEventListener('touchmove', onDragClip)
  window.removeEventListener('touchend', endDragClip)
}

const cancelCrop = () => {
  stopIntervalPreview()
  isCroppingVideoPlaying.value = false
  isCroppingMode.value = false
  if (videoInputRef.value) videoInputRef.value.value = ''
  if (croppingPreviewRef.value) croppingPreviewRef.value.src = ''
  
  // 释放 blob URL
  if (blobUrlToRevoke) {
    URL.revokeObjectURL(blobUrlToRevoke)
    blobUrlToRevoke = null
  }
  
  videoUrl.value = null
  videoDuration.value = 0
  clipStartTime.value = 0
}

const clearVideo = () => {
  stopIntervalPreview()
  isCroppingVideoPlaying.value = false
  isCroppingMode.value = false
  if (videoInputRef.value) videoInputRef.value.value = ''
  if (croppingPreviewRef.value) croppingPreviewRef.value.src = ''
  
  // 释放 blob URL
  if (blobUrlToRevoke) {
    URL.revokeObjectURL(blobUrlToRevoke)
    blobUrlToRevoke = null
  }
  
  videoUrl.value = null
  videoDuration.value = 0
  clipStartTime.value = 0
}

const loadFFmpeg = async () => {
  // 移除 FFmpeg，改用自己的视频处理函数
}

// 视频裁剪功能 - 发送裁剪参数给后端处理
const cropAndUpload = async () => {
  if (!videoUrl.value) return
  isProcessing.value = true
  try {
    console.log('===== 开始裁剪视频 =====')
    console.log('视频 URL:', videoUrl.value)
    console.log('起始时间:', clipStartTime.value, '时长:', internalDuration.value)
    
    // 检查是否可以直接从 URL 获取原文件，否则需重新上传
    if (videoUrl.value.startsWith('/media/')) {
      // 如果是本地文件 URL，需要获取原始文件
      console.log('[1/3] 当前为本地缓存 URL，需要重新上传进行裁剪...')
      
      // 先获取文件大小
      try {
        const headRes = await fetch(videoUrl.value, { method: 'HEAD' })
        const fileSize = parseInt(headRes.headers.get('content-length') || '0')
        const maxSize = 500 * 1024 * 1024 // 500MB
        
        if (fileSize > maxSize) {
          throw new Error(`视频文件过大 (${(fileSize / 1024 / 1024).toFixed(1)}MB)，最大支持 500MB`)
        }
      } catch (e) {
        console.warn('无法获取文件大小，继续处理...')
      }
    } else {
      console.log('[1/3] 从远程 URL 获取视频文件...')
    }
    
    // 构造 FormData 包含裁剪信息（注意：如果视频已存在于服务器则会再次上传，但这是唯一可靠的裁剪方式）
    // 首先从 URL 获取视频文件
    const response = await fetch(videoUrl.value)
    const videoBlob = await response.blob()
    
    const formData = new FormData()
    formData.append('video', videoBlob, 'input_video.mp4')  // 添加视频文件
    formData.append('start_time', clipStartTime.value.toString())  // 起始时间
    formData.append('duration', internalDuration.value.toString())  // 时长

    console.log('[2/3] 发送剪辑请求到后端...')
    
    // 使用现有的上传端点进行裁剪  
    const res = await fetch('/api/videos/upload/', {
      method: 'POST',
      body: formData
    })
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}))
      throw new Error(errorData.error || `服务器响应错误：${res.status}`)
    }
    
    const result = await res.json()
    console.log('裁剪结果:', result)
    
    // 释放旧的 blob URL
    if (blobUrlToRevoke) {
      URL.revokeObjectURL(blobUrlToRevoke)
      blobUrlToRevoke = null
    }
    
    isCroppingMode.value = false
    isCroppingVideoPlaying.value = false
    
    clipStartTime.value = 0
    if (croppingPreviewRef.value) croppingPreviewRef.value.src = ''
    
    // 使用后端返回的正常 URL，不是 blob URL
    videoUrl.value = result.url
    videoDuration.value = result.duration
    
    showToast('视频裁剪成功', 'success')
    
  } catch (error) {
    console.error('===== 裁剪失败 =====')
    console.error('错误详情:', error)
    const errorMessage = (error as Error).message
    showToast('裁剪失败：' + errorMessage, 'error')
  } finally { 
    isProcessing.value = false 
    console.log('[3/3] 裁剪流程结束')
  }
}

watch(internalDuration, (newDuration) => {
  if (videoUrl.value) {
    const maxStartTime = Math.max(0, videoDuration.value - newDuration)
    if (clipStartTime.value > maxStartTime) clipStartTime.value = maxStartTime
  }
})

watch(videoUrl, (newUrl, oldUrl) => {
  videoDuration.value = 0
})

onUnmounted(() => {
  if (intervalFrameId) cancelAnimationFrame(intervalFrameId)
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  if (syncAnimationFrame) cancelAnimationFrame(syncAnimationFrame)
  if (videoSyncFrame) cancelAnimationFrame(videoSyncFrame)
  if (timelinePlayInterval) clearTimeout(timelinePlayInterval)
  // 释放 blob URL
  if (blobUrlToRevoke) {
    URL.revokeObjectURL(blobUrlToRevoke)
    blobUrlToRevoke = null
  }
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
.duration-input-wrapper { display: flex; align-items: center; gap: 8px; }
.help-icon-btn { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: transparent; border: 1px solid var(--border-color); cursor: pointer; transition: all 0.2s; padding: 0; }
.help-icon-btn:hover { background: var(--accent-color); border-color: var(--accent-color); }
.help-icon { width: 20px; height: 20px; filter: brightness(0) invert(0.6); }
.help-icon-btn:hover .help-icon { filter: brightness(0) invert(1); }
.duration-input { display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 14px; }
.btn-save { padding: 8px 20px; background: var(--accent-color); color: white; border: none; border-radius: 10px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.btn-save:hover { opacity: 0.9; transform: scale(1.02); }
.btn-cancel { padding: 8px 20px; background: var(--bg-tertiary); color: var(--text-secondary); border: none; border-radius: 10px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.btn-cancel:hover { background: var(--bg-primary); color: var(--text-primary); }
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; padding-left: 58px; }
.tool-btn { padding: 8px 16px; background: var(--bg-primary); border: none; border-radius: 10px; cursor: pointer; transition: all 0.2s; font-size: 14px; }
.tool-btn.active { background: var(--accent-color); color: white; }
.tool-btn:hover { background: rgba(255, 45, 85, 0.1); }
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
.char-row.can-interact:hover .row-timeline { background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.2); cursor: pointer; }
.char-row.can-interact .row-timeline.selecting { background: rgba(255, 59, 48, 0.15); border-color: rgba(255, 59, 48, 0.3); box-shadow: 0 0 15px rgba(255, 59, 48, 0.1); }
.char-tab.disabled { opacity: 0.4; cursor: not-allowed; }
.row-selection-overlay { position: absolute; top: 0; bottom: 0; background: var(--accent-color); opacity: 0.3; border-radius: 6px; pointer-events: none; z-index: 1; }
.segments-container { position: absolute; top: 4px; left: 0; right: 0; bottom: 4px; z-index: 2; overflow: visible; }
.segment-block { position: absolute; top: 50%; transform: translateY(-50%); height: 26px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 500; font-size: 9px; white-space: nowrap; background: #636366; z-index: 1; border-right: 1px solid rgba(255, 255, 255, 0.3); box-sizing: border-box; overflow: visible; }
.segment-edge-highlight { position: absolute; top: 0; bottom: 0; width: 3px; background: #00d4ff; border-radius: 2px; box-shadow: 0 0 8px rgba(0, 212, 255, 0.8); z-index: 10; }
.segment-edge-highlight.left { left: -1px; }
.segment-edge-highlight.right { right: -1px; }
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
.dialog-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.dialog-header h3 { margin: 0; font-size: 18px; font-weight: 600; }
.dialog-close { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 50%; background: transparent; border: none; color: var(--text-secondary); cursor: pointer; transition: all 0.2s; padding: 0; }
.dialog-close:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.help-dialog { max-width: 600px; }
.help-content { max-height: 60vh; overflow-y: auto; }
.help-section { margin-bottom: 20px; }
.help-section:last-child { margin-bottom: 0; }
.help-section h4 { margin: 0 0 12px 0; font-size: 15px; font-weight: 600; color: var(--accent-color); }
.help-section ol, .help-section ul { margin: 0; padding-left: 20px; }
.help-section li { margin-bottom: 8px; font-size: 14px; color: var(--text-secondary); line-height: 1.6; }
.help-section li strong { color: var(--text-primary); }
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
.video-header-left { display: flex; align-items: center; gap: 16px; }
.video-header h3 { margin: 0; font-size: 16px; font-weight: 600; color: var(--text-primary); }
.sync-checkbox { display: inline-flex; align-items: center; }
.sync-checkbox .checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  user-select: none;
}
.sync-checkbox .checkbox-input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--accent-color);
}
.btn-clear-video { padding: 6px 12px; background: rgba(255, 59, 48, 0.15); border: none; border-radius: 6px; cursor: pointer; font-size: 12px; color: #ff3b30; transition: all 0.2s; }
.btn-clear-video:hover { background: rgba(255, 59, 48, 0.25); }
.video-upload { padding: 40px; background: var(--bg-primary); border: 2px dashed var(--border-color); border-radius: 12px; cursor: pointer; transition: all 0.2s; text-align: center; }
.video-upload:hover { border-color: var(--accent-color); background: rgba(255, 45, 85, 0.05); }
.video-input { display: none; }
.upload-hint { display: flex; flex-direction: column; align-items: center; gap: 8px; color: var(--text-secondary); }
.upload-icon { font-size: 32px; }
.video-preview { display: flex; flex-direction: column; gap: 12px; }
.video-player { width: 100%; max-height: 400px; background: #000; border-radius: 12px; object-fit: contain; }

/* 紧凑 Apple 风格裁剪弹窗 */
.crop-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
  animation: cropFadeIn 0.2s ease-out;
}

@keyframes cropFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.crop-panel {
  background: #1c1c1e;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: cropSlideUp 0.25s ease-out;
}

@keyframes cropSlideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.crop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.crop-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.crop-close {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8e8e93;
  transition: all 0.15s;
}

.crop-close:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.crop-video-wrap {
  position: relative;
  background: #000;
  width: 100%;
  aspect-ratio: 16 / 9;
}

.crop-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.crop-play-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 56px;
  height: 56px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}

.crop-play-btn:hover {
  background: rgba(255, 45, 85, 0.8);
  transform: translate(-50%, -50%) scale(1.1);
}

.crop-timeline {
  padding: 16px;
}

.crop-timeline-wrap {
  position: relative;
  padding: 8px 0;
  margin-bottom: 8px;
}

.crop-timeline-bar {
  position: relative;
  height: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.crop-timeline-left {
  position: absolute;
  left: 0;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  z-index: 1;
}

.crop-timeline-range {
  position: absolute;
  height: 4px;
  z-index: 2;
  cursor: grab;
}

.crop-timeline-range:active {
  cursor: grabbing;
}

.crop-timeline-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff2d55, #ff6b8a);
  border-radius: 2px;
}

.crop-time-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #8e8e93;
  margin-top: 8px;
}

.crop-time-duration {
  color: #ff2d55;
  font-weight: 600;
}

.crop-actions {
  display: flex;
  gap: 10px;
  padding: 12px 16px 20px;
}

.crop-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.crop-btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.crop-btn-cancel:hover {
  background: rgba(255, 255, 255, 0.15);
}

.crop-btn-confirm {
  background: #ff2d55;
  color: #fff;
  box-shadow: 0 4px 12px rgba(255, 45, 85, 0.3);
}

.crop-btn-confirm:hover:not(:disabled) {
  background: #ff375f;
  transform: scale(1.02);
  box-shadow: 0 6px 16px rgba(255, 45, 85, 0.4);
}

.crop-btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.crop-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 全屏 Loading */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner svg {
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 15px;
  font-weight: 500;
  color: #fff;
}

/* Toast 提示 */
.toast {
  position: fixed;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  z-index: 10001;
  animation: toastIn 0.3s ease-out;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.toast.success {
  background: #34c759;
}

.toast.error {
  background: #ff3b30;
}
</style>
