<template>
  <div class="chat-view">
    <!-- Disclaimer Banner -->
    <div class="disclaimer-banner">
      <q-banner class="bg-warning text-dark">
        <template v-slot:avatar>
          <q-icon name="info" color="warning" />
        </template>
        <div class="text-body1">
          AI may make mistakes. This is for informational purposes only, not legal advice.
        </div>
      </q-banner>
    </div>
    
    <div class="chat-container">
      <!-- Messages Area -->
      <q-scroll-area 
        ref="scrollArea" 
        class="messages-container"
        
      >
        <!-- Welcome Section -->
        <div v-if="messages.length === 0" class="welcome-section">
          <div class="welcome-content">
            <div class="welcome-icon">
              <q-icon name="psychology" size="80px" color="primary" />
            </div>
            <h2 class="welcome-title">How can I help you today?</h2>
            <p class="welcome-description">
              I'm here to help you understand Zambian law. Ask me anything about legal procedures, 
              rights, regulations, or any legal topic you'd like to explore.
            </p>
            
            <!-- Example Questions Grid -->
            <div class="examples-grid">
              <div 
                v-for="example in exampleQuestions"
                :key="example.question"
                @click="askExample(example.question)"
                :class="['example-card', { 'disabled': isLoading }]"
              >
                <q-icon :name="example.icon" size="24px" class="example-icon" />
                <span class="example-text">{{ example.question }}</span>
              </div>
            </div>
          </div>
        </div>        <!-- Chat Messages -->
        <div v-for="message in messages" :key="message.id" class="message-wrapper">
          <div class="message-container">
            <!-- User Message -->
            <div v-if="message.role === 'user'" class="user-message">
              <div class="message-content user-content">
                <p>{{ message.content }}</p>
              </div>
              <div class="message-avatar user-avatar">
                <q-icon name="person" size="20px" />
              </div>
            </div>
            
            <!-- AI Message -->
            <div v-else class="ai-message">
              <div class="message-avatar ai-avatar">
                <q-icon name="psychology_alt" size="20px" />
              </div>
              <div class="message-content ai-content">
                <div v-html="formatMessage(message.content)"></div>
                  <!-- Message Actions -->
                <div class="message-actions">
                  <q-btn 
                    size="sm" 
                    flat 
                    round 
                    icon="thumb_up"
                    @click="provideFeedback(message.id, 'positive')"
                    :color="message.feedback === 'helpful' ? 'positive' : 'grey-6'"
                    data-cy="thumbs-up"
                  />
                  <q-btn 
                    size="sm" 
                    flat 
                    round 
                    icon="thumb_down"
                    @click="provideFeedback(message.id, 'negative')"
                    :color="message.feedback === 'not-helpful' ? 'negative' : 'grey-6'"
                    data-cy="thumbs-down"
                  />
                  <q-btn 
                    size="sm" 
                    flat 
                    round 
                    icon="content_copy"
                    @click="copyMessage(message.content)"
                    color="grey-6"
                    data-cy="copy-message"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>        <!-- Loading indicator -->
        <div v-if="isLoading" class="loading-indicator">
          <div class="ai-message">
            <div class="message-avatar ai-avatar">
              <q-icon name="psychology_alt" size="20px" />
            </div>
            <div class="message-content ai-content">
              <div class="typing-animation">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
              </div>
              <span class="typing-text">Thinking...</span>
            </div>
          </div>
        </div>
      </q-scroll-area>

      <!-- Modern Input Section -->
      <div class="input-section">
        <!-- Added new class -->
        <div class="input-container google-inspired-input-container"> 
          <!-- Input Field and Model Selector now combined -->
          <div class="input-field-and-model-selector">
            <q-form @submit="sendMessage" class="input-form">
              <div class="input-wrapper">
                <q-input
                  ref="messageInput"
                  v-model="newMessage"
                  placeholder="Ask a question about Zambian law..."
                  borderless
                  dense
                  autogrow
                  class="message-input" 
                  :disable="isLoading"
                  @focus="onInputFocus"
                  @blur="onInputBlur"
                  @keydown.enter="handleEnterKey"
                >
                  <template v-slot:append>
                    <q-btn
                      v-if="newMessage.length > 0"
                      flat
                      round
                      dense
                      icon="send"
                      @click="sendMessage"
                      :disable="isLoading"
                      class="send-button"
                      color="primary"
                    />
                  </template>
                </q-input>
              </div>
            </q-form>

            <!-- Model Selector -->
            <!-- New wrapper for styling -->
            <div class="model-selector-wrapper"> 
              <q-select
                v-model="selectedModel"
                :options="modelOptions"
                option-value="value"
                option-label="label"
                dense
                borderless
                class="model-selector"
                popup-content-class="model-selector-popup"
                @update:model-value="handleModelChange"
              >
                <template v-slot:prepend>
                  <q-icon name="psychology" size="18px" color="grey-7" />
                </template>
                <template v-slot:selected>
                  <span class="model-label">{{ selectedModelInfo?.displayName || 'Select Model' }}</span>
                </template>
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps" class="model-option">
                    <q-item-section avatar>
                      <q-icon 
                        :name="scope.opt.installed ? 'check_circle' : 'download'" 
                        :color="scope.opt.installed ? 'positive' : 'blue'" 
                        size="sm" 
                      />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="model-name">{{ scope.opt.label }}</q-item-label>
                      <q-item-label caption class="model-description">{{ scope.opt.description }}</q-item-label>
                      <q-item-label caption class="model-size">{{ scope.opt.size }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </div>
          </div>

          <!-- Input Footer (Disclaimer) -->
          <div class="input-footer">
            <div class="disclaimer">
              AI may make mistakes. This is for informational purposes only, not legal advice.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useChatStore } from '@/stores'
import { ollamaApi, type OllamaMessage, type ModelInfo } from '@/services'
import { Notify, copyToClipboard } from 'quasar'

const route = useRoute()
const chatStore = useChatStore()

const newMessage = ref('') // Initialize newMessage
const scrollArea = ref()
const currentMessage = ref('')
const messageInput = ref()
const isLoading = ref(false)

const messages = computed(() => chatStore.currentSession?.messages || [])
const selectedModel = computed({
  get: () => chatStore.selectedModel,
  set: (value: string) => chatStore.setSelectedModel(value)
})

const availableModels = computed(() => chatStore.availableModels)
const isLoadingModels = computed(() => chatStore.isLoadingModels)

const exampleQuestions = [
  {
    question: 'What are my rights as an employee in Zambia?',
    icon: 'work'
  },
  {
    question: 'How do I get married legally in Zambia?',
    icon: 'favorite'
  },
  {
    question: 'What are the property ownership laws?',
    icon: 'home'
  },
  {
    question: 'What should I do if I\'m arrested?',
    icon: 'security'
  }
]

const modelOptions = computed(() => {
  return availableModels.value.map(model => ({
    label: model.displayName,
    value: model.name,
    description: model.description,
    size: model.size,
    installed: (model as any).installed ?? true
  }))
})

const selectedModelInfo = computed(() => {
  return availableModels.value.find(model => model.name === selectedModel.value)
})

onMounted(() => {
  // Initialize chat session
  chatStore.createSession()
  
  // Check for initial query from route
  const initialQuery = route.query.q as string
  if (initialQuery) {
    currentMessage.value = initialQuery
    sendMessage()
  }
})

// Watch for model changes to update session
watch(selectedModel, (newModel) => {
  if (chatStore.currentSession) {
    chatStore.currentSession.model = newModel
  }
})

const handleModelChange = (modelName: string) => {
  chatStore.setSelectedModel(modelName)
  
  Notify.create({
    type: 'positive',
    message: `Switched to ${selectedModelInfo.value?.displayName || modelName}`,
    position: 'top',
    timeout: 2000
  })
}

// Input focus/blur handlers
const onInputFocus = () => {
  // Optional: Add any focus behavior here
}

const onInputBlur = () => {
  // Optional: Add any blur behavior here
}

const handleEnterKey = (event: KeyboardEvent) => {
  // Regular Enter sends the message, Shift+Enter adds a new line
  if (event.shiftKey) {
    // Allow default behavior for Shift+Enter (new line)
    return
  }
  event.preventDefault()
  sendMessage()
}

const askExample = (question: string) => {
  newMessage.value = question
  sendMessage()
}

const cancelRequest = () => {
  chatStore.cancelCurrentRequest()
  isLoading.value = false
  
  Notify.create({
    type: 'info',
    message: 'Request cancelled',
    position: 'top',
    timeout: 1500
  })
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return

  const userMessage = newMessage.value.trim()
  newMessage.value = ''
  isLoading.value = true

  try {
    // Add user message to chat
    chatStore.addMessage(userMessage, 'user')

    // Scroll to bottom
    await nextTick()
    scrollToBottom()

    // Prepare messages for API
    const apiMessages: OllamaMessage[] = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    // Get AI response with selected model
    const response = await ollamaApi.chat(apiMessages, selectedModel.value)
    
    // Add AI response to chat
    chatStore.addMessage(response.message.content, 'assistant')

  } catch (error) {
    console.error('Failed to get AI response:', error)
    
    if (error instanceof Error && error.message === 'Request was cancelled') {
      return // Don't show error for cancelled requests
    }
    
    // Add error message
    chatStore.addMessage(
      'Sorry, I\'m having trouble connecting to the AI service. Please check that Ollama is running and try again.',
      'assistant'
    )
    
    Notify.create({
      type: 'negative',
      message: 'Failed to get AI response',
      position: 'top',
      timeout: 3000
    })
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const copyMessage = async (content: string) => {
  try {
    await copyToClipboard(content)
    Notify.create({
      type: 'positive',
      message: 'Message copied to clipboard',
      position: 'top',
      timeout: 1500
    })
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: 'Failed to copy message',
      position: 'top',
      timeout: 2000
    })
  }
}

const formatMessage = (content: string): string => {
  const html = marked(content, { 
    breaks: true,
    gfm: true 
  })
  return DOMPurify.sanitize(html as string)
}

const formatTimestamp = (timestamp: Date): string => {
  return timestamp.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const provideFeedback = (messageId: string, type: 'positive' | 'negative') => {
  chatStore.setMessageFeedback(messageId, type === 'positive' ? 'helpful' : 'not-helpful')
  
  Notify.create({
    type: 'info',
    message: `Thank you for your feedback!`,
    position: 'top',
    timeout: 1500
  })
}

const scrollToBottom = () => {
  if (scrollArea.value) {
    scrollArea.value.setScrollPosition('vertical', 999999, 300)
  }
}
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f0f2f5; /* Light grey background for the whole view */
}

/* Disclaimer Banner */
.disclaimer-banner {
  width: 100%;
  z-index: 5;
}

.disclaimer-banner .q-banner {
  margin-bottom: 0;
}

.chat-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Prevent chat container from causing scrollbars on body */
}

.messages-container { /* Class for q-scroll-area */
  flex-grow: 1;
  padding: 16px;
  min-height: 0; /* ADDED: Important for flex children that scroll */
}

/* Modern Header */
.chat-header {
  background: white;
  border-bottom: 1px solid #e0e4e7;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  color: #1976d2;
}

.header-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.disclaimer-chip {
  font-weight: 500;
}

/* Welcome Section */
.welcome-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.welcome-content {
  text-align: center;
  max-width: 600px;
  padding: 40px 20px;
}

.welcome-icon {
  margin-bottom: 24px;
}

.welcome-title {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16px;
  line-height: 1.3;
}

.welcome-description {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 40px;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 32px;
}

.example-card {
  background: white;
  border: 1px solid #e0e4e7;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
}

.example-card:hover:not(.disabled) {
  border-color: #1976d2;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
  transform: translateY(-2px);
}

.example-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.example-icon {
  color: #1976d2;
  flex-shrink: 0;
}

.example-text {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  line-height: 1.4;
}

/* Messages */
.message-wrapper {
  margin-bottom: 24px;
}

.message-container {
  max-width: 800px;
  margin: 0 auto;
}

.user-message, .ai-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar {
  background: #1976d2;
  color: white;
}

.ai-avatar {
  background: transparent; /* Remove background */
  color: #1976d2; /* Blue color for agent icon */
}

.message-content {
  max-width: 70%;
  border-radius: 16px;
  padding: 12px 16px;
  position: relative;
}

.user-content {
  background: #1976d2;
  color: white;
  border-bottom-right-radius: 4px;
  font-weight: 500; /* Make text more readable */
}

.ai-content {
  background: white;
  border: 1px solid #e0e4e7;
  color: #1a1a1a;
  border-bottom-left-radius: 4px;
}

.user-content p {
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
  letter-spacing: 0.01em; /* Slightly improve readability */
}

.ai-content :deep(p) {
  margin: 0 0 12px 0;
  font-size: 14px;
  line-height: 1.6;
}

.ai-content :deep(p:last-child) {
  margin-bottom: 0;
}

.ai-content :deep(ul), .ai-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.ai-content :deep(li) {
  margin: 4px 0;
  line-height: 1.5;
}

.ai-content :deep(strong) {
  font-weight: 600;
  color: #1a1a1a;
}

.ai-content :deep(code) {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
}

.ai-content :deep(pre) {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  margin: 12px 0;
  overflow-x: auto;
}

.message-actions {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.ai-message:hover .message-actions {
  opacity: 1;
}

/* Loading Animation */
.loading-indicator {
  margin-bottom: 24px;
}

.typing-animation {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1976d2;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.typing-text {
  font-size: 13px;
  color: #666;
  font-style: italic;
}

/* Modern Input Section */
.input-section {
  padding: 8px 16px 16px 16px; 
  background-color: #f0f2f5; 
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: center;
  flex-shrink: 0; /* ADDED: Prevent this section from shrinking */
}

.google-inspired-input-container { /* New class for the main input bubble */
  width: 100%;
  max-width: 700px; /* Max width for the input area */
  background-color: #fff;
  border-radius: 28px; /* More pronounced rounding */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 8px 16px;
  display: flex;
  flex-direction: column;
}

.input-field-and-model-selector {
  display: flex;
  flex-direction: column; /* Stack input and model selector */
}

.input-form {
  width: 100%;
  display: flex;
  align-items: center;
}

.input-wrapper {
  flex-grow: 1;
}

.message-input .q-field__control {
  background-color: white !important; /* White background */
  box-shadow: none !important;
  border: none !important; /* Remove any borders */
}

.message-input .q-field__native {
  padding-left: 8px !important; /* Adjust padding if needed */
}

.send-button {
  margin-left: 8px;
}

.model-selector-wrapper {
  display: flex;
  align-items: center;
  padding-top: 2px; /* Reduced space between input and model selector */
  padding-bottom: 4px; /* Space below model selector */
  /* Removed border-top divider line */
  margin-top: 4px; /* Reduced space above */
}

.model-selector {
  width: auto !important; /* Allow it to size based on content */
  font-size: 0.85em;
  max-width: 180px; /* Limit width for pill style */
}

.model-selector .q-field__control {
  background-color: #e0e0e0 !important; /* Darker gray pill background */
  border-radius: 20px !important; /* More rounded pill shape */
  min-height: 32px !important; /* Smaller height for pill */
  padding: 0 12px !important;
  border: none !important;
}

.model-selector .q-field__prepend {
  padding-right: 6px; /* Space after icon */
}

.model-label {
  font-size: 0.9em;
  color: #5f6368; /* Google-like text color */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.input-footer {
  text-align: center;
  padding-top: 8px;
}

.disclaimer {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* Model Selector Popup */
.model-selector-popup {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid #e0e4e7;
  max-height: 400px;
}

.model-option {
  padding: 12px 16px;
  border-radius: 8px;
  margin: 4px 8px;
}

.model-option:hover {
  background: #f8f9fa;
}

.model-name {
  font-weight: 500;
  color: #1a1a1a;
}

.model-description {
  color: #666;
  font-size: 12px;
  margin-top: 2px;
}

.model-size {
  color: #999;
  font-size: 11px;
  margin-top: 2px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .chat-header {
    padding: 12px 16px;
  }
  
  .header-title {
    font-size: 20px;
  }
  
  .messages-container {
    padding: 16px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .examples-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .example-card {
    padding: 16px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .input-section {
    padding: 16px;
  }
  
  .model-selector {
    max-width: 100%;
  }
  
  .input-footer {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .welcome-content {
    padding: 20px 16px;
  }
  
  .welcome-title {
    font-size: 20px;
  }
  
  .welcome-description {
    font-size: 14px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .message-content {
    max-width: 90%;
    font-size: 14px;
  }
}
</style>
