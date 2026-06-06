<template>
  <div class="h-[calc(100vh-100px)] flex flex-col bg-gray-50 border rounded-lg overflow-hidden">
    <!-- 头部 -->
    <div class="bg-white border-b border-gray-200 px-6 py-3">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-800">AI 对话助手</h2>
        <button
          @click="clearMessages"
          class="text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          清空对话
        </button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50"
    >
      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[70%] px-4 py-3 rounded-2xl"
          :class="
            msg.role === 'user'
              ? 'bg-blue-500 text-white rounded-br-md'
              : 'bg-white text-gray-800 rounded-bl-md shadow-sm'
          "
        >
          <div
            class="text-xs mb-1"
            :class="msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'"
          >
            {{ msg.role === 'user' ? '我' : 'AI 助手' }}
          </div>
          <p class="text-sm whitespace-pre-wrap">{{ msg.content }}</p>
          <div
            v-if="msg.timestamp"
            class="text-xs mt-1 opacity-60"
          >
            {{ msg.timestamp }}
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="flex justify-start">
        <div class="bg-white px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="bg-white border-t border-gray-200 p-4">
      <div class="flex items-center space-x-4">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="输入消息..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          :disabled="isLoading"
        />
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim() || isLoading"
          class="px-6 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
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

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value)
    return

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

  // 创建 AI 消息对象（用于流式更新）
  const aiMsg = {
    role: 'assistant',
    content: '',
    timestamp: new Date().toLocaleTimeString()
  }
  messages.value.push(aiMsg)
  
  // 获取 AI 消息在数组中的索引，用于响应式更新
  const aiMsgIndex = messages.value.length - 1

  try {
    // 使用 fetch API 处理流式响应
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

    // 处理流式响应
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
              // 实际输出文本 - 使用索引更新以确保响应式
              messages.value[aiMsgIndex] = {
                ...messages.value[aiMsgIndex],
                content: messages.value[aiMsgIndex].content + data.content
              }
              await nextTick()
              scrollToBottom()
            } else if (data.type === 'done') {
              // 完成 - 设置标志并退出循环
              isDone = true
              break
            } else if (data.type === 'error') {
              // 错误处理
              throw new Error(data.content || '服务器错误')
            }
          } catch (e) {
            // JSON 解析错误，忽略
          }
        }
      }
    }

    // 如果没有收到任何内容，显示默认消息
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

const clearMessages = () => {
  messages.value = [
    {
      role: 'assistant',
      content: '你好！我是你的 AI 助手，有什么可以帮助你的吗？',
      timestamp: new Date().toLocaleTimeString()
    }
  ]
}
</script>

<style scoped>
.h-full {
  height: 100%;
}
.flex {
  display: flex;
}
.flex-col {
  flex-direction: column;
}
.flex-1 {
  flex: 1;
}
.space-y-4 > * + * {
  margin-top: 16px;
}
.space-x-4 > * + * {
  margin-left: 16px;
}
.justify-end {
  justify-content: flex-end;
}
.justify-start {
  justify-content: flex-start;
}
.overflow-y-auto {
  overflow-y: auto;
}
.bg-gray-50 {
  background-color: #f9fafb;
}
.bg-white {
  background-color: white;
}
.bg-blue-500 {
  background-color: #3b82f6;
}
.bg-gray-300 {
  background-color: #d1d5db;
}
.text-white {
  color: white;
}
.text-gray-800 {
  color: #1f2937;
}
.text-gray-500 {
  color: #6b7280;
}
.text-red-500 {
  color: #ef4444;
}
.text-sm {
  font-size: 0.875rem;
}
.text-xl {
  font-size: 1.25rem;
}
.font-semibold {
  font-weight: 600;
}
.border-b {
  border-bottom: 1px solid;
}
.border-t {
  border-top: 1px solid;
}
.border-gray-200 {
  border-color: #e5e7eb;
}
.border-gray-300 {
  border-color: #d1d5db;
}
.px-6 {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}
.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}
.py-4 {
  padding-top: 1rem;
  padding-bottom: 1rem;
}
.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}
.py-3 {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}
.w-2 {
  width: 0.5rem;
}
.h-2 {
  height: 0.5rem;
}
.rounded-xl {
  border-radius: 0.75rem;
}
.rounded-2xl {
  border-radius: 1rem;
}
.rounded-br-md {
  border-bottom-right-radius: 0.375rem;
}
.rounded-bl-md {
  border-bottom-left-radius: 0.375rem;
}
.rounded-full {
  border-radius: 9999px;
}
.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.transition-colors {
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out;
}
.cursor-not-allowed {
  cursor: not-allowed;
}
.p-6 {
  padding: 1.5rem;
}
.p-4 {
  padding: 1rem;
}
.max-w-\[70\%\] {
  max-width: 70%;
}
.focus\:outline-none:focus {
  outline: none;
}
.focus\:ring-2:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}
.focus\:ring-blue-500:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}
.focus\:border-transparent:focus {
  border-color: transparent;
}
.hover\:bg-blue-600:hover {
  background-color: #2563eb;
}
.hover\:text-red-500:hover {
  color: #ef4444;
}
.opacity-60 {
  opacity: 0.6;
}
.animate-bounce {
  animation: bounce 0.6s infinite;
}
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}
</style>