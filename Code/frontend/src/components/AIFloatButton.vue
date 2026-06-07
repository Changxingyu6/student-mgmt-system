<template>
  <div
    class="ai-float-container"
    :style="containerStyle"
  >
    <!-- 悬浮球按钮 -->
    <button
      @click="handleClick"
      @mousedown="startDrag"
      class="float-button"
      :class="{ 'active': isOpen, 'dragging': isDragging }"
    >
      <img src="@/image/image.png" alt="AI 助手" class="float-icon" />
    </button>

    <!-- AI 对话窗口 -->
    <transition name="slide-up">
      <div v-if="isOpen" class="chat-modal">
        <div class="chat-header">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <el-icon class="text-blue-500"><User /></el-icon>
              <span class="font-semibold">AI 助手</span>
            </div>
            <button @click="isOpen = false" class="close-btn">
              <span class="close-icon">×</span>
            </button>
          </div>
        </div>

        <div
          ref="messagesContainer"
          class="chat-messages"
        >
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message"
            :class="msg.role === 'user' ? 'user-message' : 'ai-message'"
          >
            <div class="message-content">
              <span class="text-xs opacity-60 mb-1 block">
                {{ msg.role === 'user' ? '我' : 'AI 助手' }}
              </span>
              <p class="whitespace-pre-wrap">{{ msg.content }}</p>
              <span v-if="msg.timestamp" class="text-xs opacity-40 mt-1 block">
                {{ msg.timestamp }}
              </span>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="isLoading" class="ai-message">
            <div class="message-content">
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input">
          <input
            v-model="inputMessage"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="输入消息..."
            class="input-field"
            :disabled="isLoading"
          />
          <button
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isLoading"
            class="send-btn"
          >
            <el-icon><Plus /></el-icon>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { User, Plus } from '@element-plus/icons-vue'

const userStore = useUserStore()
const isOpen = ref(false)
const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是你的 AI 助手，有什么可以帮助你的吗？',
    timestamp: new Date().toLocaleTimeString()
  }
])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)

// 拖拽相关状态
const isDragging = ref(false)
const position = ref({ x: window.innerWidth - 75, y: window.innerHeight - 75 })
const dragOffset = ref({ x: 0, y: 0 })

const containerStyle = computed(() => ({
  position: 'fixed',
  left: `${position.value.x}px`,
  top: `${position.value.y}px`,
  zIndex: 1000
}))

const startDrag = (e) => {
  isDragging.value = true
  dragOffset.value = {
    x: e.clientX - position.value.x,
    y: e.clientY - position.value.y
  }
}

const handleDrag = (e) => {
  if (!isDragging.value) return

  let newX = e.clientX - dragOffset.value.x
  let newY = e.clientY - dragOffset.value.y

  // 限制在视窗内
  const containerWidth = 45
  const containerHeight = 45
  newX = Math.max(0, Math.min(newX, window.innerWidth - containerWidth))
  newY = Math.max(0, Math.min(newY, window.innerHeight - containerHeight))

  position.value = { x: newX, y: newY }
}

const stopDrag = () => {
  isDragging.value = false
}

const handleClick = () => {
  if (isDragging.value) return
  toggleChat()
}

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMsg = {
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date().toLocaleTimeString()
  }
  messages.value.push(userMsg)
  inputMessage.value = ''

  await nextTick()
  scrollToBottom()

  isLoading.value = true

  const aiMsg = {
    role: 'assistant',
    content: '',
    timestamp: new Date().toLocaleTimeString()
  }
  messages.value.push(aiMsg)
  const aiMsgIndex = messages.value.length - 1

  try {
    const response = await fetch('http://localhost:8000/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({
        messages: messages.value.slice(0, -1).filter(msg => msg.role === 'user').map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`请求失败: ${errorText}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let isDone = false

    while (!isDone) {
      const { done: readerDone, value } = await reader.read()

      if (readerDone) {
        isDone = true
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'text') {
              messages.value[aiMsgIndex] = {
                ...messages.value[aiMsgIndex],
                content: messages.value[aiMsgIndex].content + data.content
              }
              await nextTick()
              scrollToBottom()
            } else if (data.type === 'done') {
              isDone = true
              break
            } else if (data.type === 'error') {
              throw new Error(data.content || '服务器错误')
            }
          } catch (e) {
            // JSON 解析错误，忽略
          }
        }
      }
    }

    if (!messages.value[aiMsgIndex].content) {
      messages.value[aiMsgIndex] = {
        ...messages.value[aiMsgIndex],
        content: '暂无回复'
      }
    }
  } catch (error) {
    console.error('AI 请求失败:', error)
    messages.value[aiMsgIndex] = {
      ...messages.value[aiMsgIndex],
      content: '抱歉，请求失败，请稍后重试。'
    }
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

import { nextTick } from 'vue'

onMounted(() => {
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.ai-float-container {
  transition: none;
}

.float-button {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: white;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.float-button:hover {
  transform: scale(1.05);
  border-color: #e0e0e0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.float-button.dragging {
  cursor: grabbing;
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.float-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.float-button.active {
  transform: rotate(45deg);
}

.float-button.active.dragging {
  transform: rotate(45deg) scale(1.1);
}

.icon {
  font-size: 24px;
  color: white;
}

.chat-modal {
  position: absolute;
  right: 0;
  bottom: 80px;
  width: 400px;
  max-height: 500px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 4px;
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 20px;
  line-height: 1;
}

.close-icon {
  font-size: 20px;
  font-weight: bold;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
}

.message {
  display: flex;
  margin-bottom: 16px;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.message-content {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 16px;
}

.user-message .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-message .message-content {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.chat-input {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 12px;
}

.input-field {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  outline: none;
  font-size: 14px;
  transition: all 0.2s;
}

.input-field:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.input-field:disabled {
  background: #f5f5f5;
  color: #999;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 加载动画 */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.animate-bounce {
  animation: bounce 0.6s infinite;
}
</style>