<template>
  <div class="rotation-player">
    <div class="timeline">
      <div class="global-playhead-track" @mousedown="startDragGlobal" @mousemove="onDragGlobal" @mouseup="endDragGlobal" @mouseleave="endDragGlobal">
        <div class="global-playhead" :style="{ left: progressPercent + '%' }">
          <div class="playhead-handle"></div>
        </div>
      </div>
      
      <div class="time-scale">
        <span 
          v-for="s in gridSeconds" 
          :key="s" 
          class="time-scale-label"
          :style="{ left: ((s - 1) / rotation.totalDuration * 100) + '%' }"
        >
          {{ s - 1 }}
        </span>
      </div>
      
      <div 
        v-for="(character, charIndex) in rotation.characters" 
        :key="character.name"
        class="timeline-row"
        @click="seekToRow($event)"
      >
        <div class="row-label" :class="{ active: activeCharacter === character.name }">
          <img :src="'/assets/characters/' + character.name + '.webp'" :alt="character.name" @error="$event.target.style.display='none'">
        </div>
        
        <div class="row-timeline">
          <div class="row-played-bg" :style="{ width: progressPercent + '%' }"></div>
          
          <div class="row-grid">
            <div 
              v-for="s in gridSeconds" 
              :key="s" 
              class="grid-cell"
              :style="{ left: ((s - 1) / rotation.totalDuration * 100) + '%' }"
            ></div>
          </div>
          
          <div class="segments-container">
            <template v-for="(segment, segIndex) in getMergedSegmentsWithVariation(character.name, character.segments)">
              <a-tooltip 
                v-if="(segment.type !== 'switch' && segment.description) || segment.isVariationSeg" 
                placement="top"
                :mouseEnterDelay="0"
                :showAfter="0"
                :overlayClassName="'segment-tooltip'"
                :getPopupContainer="(trigger) => trigger.parentElement"
              >
                <template #title>
                  {{ segment.isVariationSeg ? '变奏' : segment.description }}
                </template>
                <div
                  :key="'seg-' + segIndex"
                  ref="segmentRefs"
                  class="segment-block"
                  :class="{ 
                    active: currentSegment?.character === character.name && 
                           ((currentSegment?.startTime || currentSegment?.time || 0) >= segment.startTime && 
                           (currentSegment?.startTime || currentSegment?.time || 0) < segment.endTime),
                    completed: segment.startTime <= currentTime,
                    'is-variation': segment.isVariationSeg
                  }"
                  :style="{
                    left: (segment.startTime / rotation.totalDuration * 100) + '%',
                    width: (segment.endTime - segment.startTime) / rotation.totalDuration * 100 + '%'
                  }"
                  @mouseenter="handleMouseEnter"
                  @mouseleave="handleMouseLeave"
                >
                  <span class="segment-label">{{ segment.display }}</span>
                </div>
              </a-tooltip>
              <div 
                v-else-if="segment.type !== 'switch' || segment.isVariationSeg"
                :key="'seg-' + segIndex"
                ref="segmentRefs"
                class="segment-block"
                :class="{ 
                  active: currentSegment?.character === character.name && 
                         ((currentSegment?.startTime || currentSegment?.time || 0) >= segment.startTime && 
                         (currentSegment?.startTime || currentSegment?.time || 0) < segment.endTime),
                  completed: segment.startTime <= currentTime,
                  'is-variation': segment.isVariationSeg
                }"
                :style="{
                  left: (segment.startTime / rotation.totalDuration * 100) + '%',
                  width: (segment.endTime - segment.startTime) / rotation.totalDuration * 100 + '%'
                }"
                @mouseenter="handleMouseEnter"
                @mouseleave="handleMouseLeave"
              >
                <span class="segment-label">{{ segment.display }}</span>
              </div>
            </template>
          </div>
          
          <template v-for="(segment, segIndex) in character.segments" :key="segIndex">
            <div 
              v-if="segment.type === 'switch' && !segment.endTime"
              class="switch-arrow-container"
              :class="[getTargetCharIndex(segment.target) < charIndex ? 'arrow-up' : 'arrow-down']"
              :style="{ 
                left: ((segment.time !== undefined ? segment.time : segment.startTime || 0) / rotation.totalDuration * 100) + '%',
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
              :class="[segment.endTime ? (getTargetCharIndex(segment.target) < charIndex ? 'arrow-up' : 'arrow-down') : '']"
              :style="{ 
                left: ((segment.time !== undefined ? segment.time : segment.startTime || 0) / rotation.totalDuration * 100) + '%',
                '--arrow-height': (Math.abs(getTargetCharIndex(segment.target) - charIndex) * 72 - 42) + 'px'
              }"
            >
              <div class="switch-arrow-line"></div>
              <img src="/assets/triangle_down_fill.svg" class="switch-arrow-head" />
              <span class="switch-arrow-label">变奏 -{{ segment.target }}</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <div class="current-action">
      <span class="label">当前操作:</span>
      <span class="value" :key="currentSegment?.startTime || currentSegment?.time">
        {{ currentSegment?.display || '等待中...' }}
      </span>
      <span v-if="currentSegment" class="current-time-label">
        {{ currentSegment?.character }} · {{ currentSegment?.description }} · {{ currentSegment?.startTime?.toFixed(1) }}-{{ currentSegment?.endTime?.toFixed(1) }}秒
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'

interface Segment {
  type: 'action' | 'switch'
  startTime?: number
  endTime?: number
  time?: number
  display: string
  description?: string
  target?: string
}

interface MergedSegment {
  startTime: number
  endTime: number
  display: string
  description: string
  count: number
  type?: 'action' | 'switch'
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

const props = defineProps<{
  rotation: Rotation
  currentTime: number
}>()

let isDragging = false
const segmentRefs = ref<HTMLElement[]>([])
let lastActiveIndex = -1

const updateSegmentWidths = (force = false) => {
  const currentActiveIdx = currentSegmentIndex.value
  if (!force && currentActiveIdx === lastActiveIndex && !isDragging) return
  
  nextTick(() => {
    segmentRefs.value.forEach((el) => {
      if (el) {
        const isActive = el.classList.contains('active') || el.matches(':hover')
        if (isActive) {
          const label = el.querySelector('.segment-label') as HTMLElement
          if (label) {
            const textWidth = label.scrollWidth
            el.style.minWidth = `${textWidth + 12}px`
          }
        } else {
          el.style.minWidth = '0'
        }
      }
    })
  })
  lastActiveIndex = currentActiveIdx
}

const handleMouseEnter = () => {
  updateSegmentWidths(true)
}

const handleMouseLeave = () => {
  updateSegmentWidths(true)
}

watch(() => props.currentTime, () => {
  nextTick(() => updateSegmentWidths())
}, { immediate: true, deep: true })

const gridSeconds = computed(() => Math.ceil(props.rotation.totalDuration))

const getMergedSegments = (segments: Segment[]): MergedSegment[] => {
  const actions = segments.filter(s => s.type === 'action')
  const switches = segments.filter(s => s.type === 'switch')
  
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
      description: action.description,
      count,
      type: 'action'
    })
    
    i += count
  }
  
  switches.forEach(sw => {
    const hasEndTime = sw.endTime !== undefined && sw.endTime > (sw.time || 0)
    if (hasEndTime) {
      merged.push({
        startTime: sw.time || 0,
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
  props.rotation.characters.forEach(char => {
    char.segments.forEach(seg => {
      if (seg.type === 'switch' && seg.endTime && seg.target === characterName) {
        variationSegs.push({
          startTime: seg.time ?? seg.startTime ?? 0,
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
  const baseSegments = getMergedSegments(segments)
  const variationSegs = getVariationSegments(characterName)
  return [...baseSegments, ...variationSegs].sort((a, b) => a.startTime - b.startTime)
}

const allSegments = computed(() => {
  const chars = props.rotation.characters
  const segments: (Segment & { character: string })[] = []
  chars.forEach(char => {
    char.segments.forEach(seg => {
      if (seg.type === 'switch' && seg.endTime && seg.target) {
        segments.push({ 
          ...seg, 
          character: char.name,
          display: `变奏 - ${seg.target}`
        })
      } else {
        segments.push({ ...seg, character: char.name })
      }
    })
  })
  return segments.sort((a, b) => {
    const aTime = a.startTime || a.time || 0
    const bTime = b.startTime || b.time || 0
    return aTime - bTime
  })
})

const currentSegmentIndex = computed(() => {
  const time = props.currentTime
  const idx = allSegments.value.findIndex(s => {
    const segTime = s.startTime || s.time || 0
    const segEnd = s.endTime || s.time || 0
    return segEnd > time
  })
  return idx === -1 ? allSegments.value.length - 1 : idx
})

const currentSegment = computed(() => allSegments.value[currentSegmentIndex.value])

const activeCharacter = computed(() => currentSegment.value?.character || '')

const getTargetCharIndex = (targetName: string): number => {
  return props.rotation.characters.findIndex(c => c.name === targetName)
}

const progressPercent = computed(() => 
  (props.currentTime / props.rotation.totalDuration) * 100
)

const seekToRow = (event: MouseEvent) => {
  if (isDragging) return
  const container = (event.currentTarget as HTMLElement).querySelector('.row-timeline') as HTMLElement
  if (!container) return
  const rect = container.getBoundingClientRect()
  const percent = Math.max(0, Math.min((event.clientX - rect.left) / rect.width, 1))
  emit('seek', percent * props.rotation.totalDuration)
}

const seekToGlobal = (event: MouseEvent) => {
  const container = (event.currentTarget as HTMLElement)
  const rect = container.getBoundingClientRect()
  const percent = Math.max(0, Math.min((event.clientX - rect.left) / rect.width, 1))
  emit('seek', percent * props.rotation.totalDuration)
}

const startDragGlobal = (event: MouseEvent) => {
  isDragging = true
  seekToGlobal(event)
}

const onDragGlobal = (event: MouseEvent) => {
  if (!isDragging) return
  event.preventDefault()
  seekToGlobal(event)
}

const endDragGlobal = () => {
  isDragging = false
}

const emit = defineEmits<{
  (e: 'seek', time: number): void
}>()

defineExpose({
  play: () => {},
  pause: () => {},
  reset: () => {},
  seekTo: (time: number) => emit('seek', time)
})
</script>

<style scoped>
.rotation-player {
  width: 100%;
}

.timeline {
  background: var(--bg-tertiary);
  border-radius: 0;
  padding: 16px 12px;
  margin-bottom: 24px;
  position: relative;
  padding-top: 40px;
}

.global-playhead-track {
  position: absolute;
  top: 24px;
  left: 70px;
  right: 11px;
  bottom: 0;
  z-index: 50;
  cursor: grab;
}

.global-playhead-track:active {
  cursor: grabbing;
}

.global-playhead {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  transform: translateX(-50%);
  pointer-events: none;
}

.global-playhead::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 1px;
  height: 100%;
  background: rgba(255, 255, 255, 1);
}

.time-scale {
  position: absolute;
  top: 0;
  left: 70px;
  right: 0;
  height: 24px;
  z-index: 51;
  pointer-events: none;
}

.time-scale-label {
  position: absolute;
  top: 0;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
  transform: translateX(-50%);
  user-select: none;
  -webkit-user-select: none;
}

.timeline-row {
  display: flex;
  align-items: center;
  height: 48px;
  margin-bottom: 24px;
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
}
.timeline-row:last-child { margin-bottom: 0; }

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
}
.row-label img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
}
.row-label.active { 
  background: var(--accent-color);
  color: white;
}

.row-timeline {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  background: var(--bg-primary);
  border-radius: 0;
  overflow: visible;
  height: 36px;
}

.row-played-bg {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.08);
  z-index: 0;
}

.row-grid {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  pointer-events: none;
  z-index: 1;
}
.grid-cell {
  position: absolute;
  top: 0; bottom: 0;
  width: 1px;
  background: rgba(255, 255, 255, 0.06);
}
.grid-label {
  position: absolute;
  bottom: -20px;
  left: 2px;
  font-size: 10px;
  color: var(--text-tertiary);
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

.segments-container {
  position: absolute;
  top: 4px;
  left: 0;
  right: 0;
  bottom: 4px;
  z-index: 2;
}

.segment-block {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 26px;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 9px;
  transition: background-color 0.15s, box-shadow 0.15s, min-width 0.15s;
  overflow: visible;
  background: #636366;
  z-index: 1;
  white-space: nowrap;
  border-right: 1px solid var(--bg-tertiary);
}
.segment-block:last-child {
  border-right: none;
}
.segment-block.completed {
  background: #34c759;
}
.segment-block.is-variation {
  background: #ff9500;
}
.segment-block.active {
  background: #007aff;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
  overflow: visible;
  padding: 0 6px;
  border-right: 1px solid var(--bg-tertiary);
}
.segment-block.active.is-variation {
  background: #ff9500;
  box-shadow: 0 2px 8px rgba(255, 149, 0, 0.3);
}
.segment-block:hover {
  background: #ff9500;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(255, 149, 0, 0.2);
  overflow: visible;
  padding: 0 6px;
  border-right: 1px solid var(--bg-tertiary);
}
.segment-label {
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
.segment-block.active .segment-label,
.segment-block:hover .segment-label {
  overflow: visible;
  text-overflow: none;
}

.row-playhead {
  position: absolute;
  top: 0; bottom: 0;
  width: 2px;
  background: white;
  z-index: 20;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.switch-arrow-container {
  position: absolute;
  top: 100%;
  left: 0;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 5;
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
  font-size:11px;
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
  top:0px;
  bottom: auto;
}

.current-action {
  background: var(--bg-tertiary);
  padding: 10px 16px;
  border-radius: 10px;
  margin-bottom: 16px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

:deep(.segment-tooltip) {
  z-index: 10000 !important;
}
.current-action .label { color: var(--text-secondary); font-size: 13px; }
.current-action .value { color: var(--accent-color); font-weight: 600; font-size: 15px; }
.current-time-label {
  display: block;
  color: var(--text-tertiary);
  font-size: 12px;
  margin-top: 0;
}
</style>