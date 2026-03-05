<template>
  <div class="test-edit-action p-6">
    <button @click="showEditor = true" class="open-btn">
      📝 打开编辑器
    </button>

    <Teleport to="body">
      <div v-if="showEditor" class="editor-overlay" @click.self="showEditor = false">
        <div class="editor-modal">
          <div class="editor-header">
            <h2 class="text-xl font-semibold">输出轴编辑器</h2>
            <button @click="showEditor = false" class="close-btn">✕</button>
          </div>
          <div class="editor-content">
            <RotationEdit
              :characters="characters"
              :total-duration="totalDuration"
              @save="handleSave"
              @cancel="handleCancel"
            />
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import RotationEdit from './RotationEdit.vue'
import { ref } from 'vue'

const showEditor = ref(false)
const characters = ref(['漂泊者·湮灭', '散华', '维里奈'])
const totalDuration = ref(28)

const handleSave = (data: any) => {
  console.log('保存数据:', data)
  showEditor.value = false
  alert('已保存！查看控制台输出')
}

const handleCancel = () => {
  console.log('取消编辑')
  showEditor.value = false
}
</script>

<style scoped>
.test-edit-action {
  max-width: 1200px;
  margin: 0 auto;
}

.open-btn {
  padding: 14px 28px;
  font-size: 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.open-btn:hover {
  opacity: 0.9;
  transform: scale(1.02);
}

.editor-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.editor-modal {
  background: var(--bg-secondary);
  border-radius: 16px;
  width: 100%;
  max-width: 1400px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5);
  border: 1px solid var(--border-color);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

.editor-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: var(--bg-tertiary);
  border: none;
  color: var(--text-secondary);
  font-size: 20px;
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.editor-content {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}
</style>
