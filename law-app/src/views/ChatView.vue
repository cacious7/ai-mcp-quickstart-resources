<template>
  <div class="chat-view">
    <!-- Chat Header -->
    <q-toolbar class="bg-primary text-white">
      <q-toolbar-title>
        <q-icon name="chat" size="24px" class="q-mr-sm" />
        Ask Legal Questions
      </q-toolbar-title>
      <q-chip color="white" text-color="primary" icon="info">
        General Information Only
      </q-chip>
    </q-toolbar>

    <!-- Chat Container -->
    <div class="chat-container">
      <!-- Messages Area -->
      <q-scroll-area 
        ref="scrollArea" 
        class="messages-container q-pa-md"
        style="height: calc(100vh - 200px);"
      >
        <!-- Welcome Message -->
        <div v-if="messages.length === 0" class="welcome-section">
          <q-card class="welcome-card q-mb-lg">
            <q-card-section class="text-center q-pa-xl">
              <q-icon name="smart_toy" size="64px" color="primary" class="q-mb-md" />
              <h3 class="text-h5 q-mb-md">Welcome to the Legal AI Assistant</h3>
              <p class="text-body1 text-grey-7 q-mb-lg">
                Ask me anything about Zambian law in plain language. I'll provide simplified explanations with proper citations.
              </p>
              
              <q-separator class="q-my-lg" />
              
              <h4 class="text-h6 q-mb-md">Example questions:</h4>
              <div class="row q-gutter-sm justify-center">
                <q-btn 
                  v-for="example in exampleQuestions"
                  :key="example"
                  @click="askExample(example)"
                  :disable="isLoading"
                  color="primary"
                  outline
                  no-caps
                  class="example-btn"
                >
                  {{ example }}
                </q-btn>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Chat Messages -->
        <div v-for="message in messages" :key="message.id" class="message-wrapper q-mb-md">
          <q-chat-message
            :sent="message.role === 'user'"
            :bg-color="message.role === 'user' ? 'primary' : 'grey-3'"
            :text-color="message.role === 'user' ? 'white' : 'dark'"
            :name="message.role === 'user' ? 'You' : 'Legal AI'"
            :avatar="message.role === 'user' ? undefined : '/favicon.svg'"
            :stamp="formatTimestamp(message.timestamp)"
          >
            <div v-if="message.role === 'user'" class="user-message">
              {{ message.content }}
            </div>
            <div v-else class="ai-message" v-html="formatMessage(message.content)"></div>
          </q-chat-message>
          
          <!-- Message Actions -->
          <div v-if="message.role === 'assistant'" class="message-actions q-mt-sm">
            <q-btn 
              size="sm" 
              flat 
              round 
              icon="thumb_up"
              @click="provideFeedback(message.id, 'positive')"
              color="grey-6"
            />
            <q-btn 
              size="sm" 
              flat 
              round 
              icon="thumb_down"
              @click="provideFeedback(message.id, 'negative')"
              color="grey-6"
            />
          </div>
        </div>

        <!-- Loading indicator -->
        <div v-if="isLoading" class="loading-indicator q-mb-md">
          <q-chat-message
            name="Legal AI"
            avatar="/favicon.svg"
            bg-color="grey-3"
          >
            <div class="typing-indicator">
              <q-spinner-dots size="20px" color="primary" />
              <span class="q-ml-sm">Thinking...</span>
            </div>
          </q-chat-message>
        </div>
      </q-scroll-area>

      <!-- Input Area -->
      <q-separator />
      <div class="input-container q-pa-md">
        <q-form @submit="sendMessage" class="row q-gutter-sm items-end">
          <div class="col">
            <q-input
              v-model="currentMessage"
              placeholder="Ask a question about Zambian law..."
              outlined
              dense
              autogrow
              :max-height="100"
              :disable="isLoading"
              @keydown.enter.prevent="sendMessage"
            >
              <template v-slot:prepend>
                <q-icon name="help" color="grey-6" />
              </template>
            </q-input>
          </div>
          <div>
            <q-btn
              type="submit"
              :disable="!currentMessage.trim() || isLoading"
              icon="send"
              color="primary"
              round
              size="md"
            />
          </div>
        </q-form>
        
        <!-- Disclaimer -->
        <div class="disclaimer q-mt-sm">
          <q-icon name="info" size="16px" color="warning" class="q-mr-xs" />
          <span class="text-caption text-grey-7">
            This AI provides general information only and is not a substitute for professional legal advice.
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useChatStore } from '@/stores'
import { ollamaApi } from '@/services'
import type { OllamaMessage } from '@/services'

const route = useRoute()
const chatStore = useChatStore()

const scrollArea = ref()
const currentMessage = ref('')
const isLoading = ref(false)

const messages = computed(() => chatStore.currentSession?.messages || [])

const exampleQuestions = [
  'What are my rights as an employee in Zambia?',
  'How do I get married legally in Zambia?',
  'What are the property ownership laws?',
  'What should I do if I\'m arrested?'
]

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

const askExample = (question: string) => {
  currentMessage.value = question
  sendMessage()
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isLoading.value) return

  const userMessage = currentMessage.value.trim()
  currentMessage.value = ''
  isLoading.value = true

  try {    // Add user message to chat
    chatStore.addMessage(userMessage, 'user')

    // Scroll to bottom
    await nextTick()
    scrollToBottom()

    // Prepare messages for API
    const apiMessages: OllamaMessage[] = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    // Get AI response
    const response = await ollamaApi.chat(apiMessages)
    
    // Add AI response to chat
    chatStore.addMessage(response.message.content, 'assistant')

  } catch (error) {
    console.error('Failed to get AI response:', error)
      // Add error message
    chatStore.addMessage('Sorry, I\'m having trouble connecting to the AI service. Please check that Ollama is running and try again.', 'assistant')
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
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
  console.log(`Feedback for message ${messageId}: ${type}`)
  // TODO: Implement feedback collection
}

const scrollToBottom = () => {
  if (scrollArea.value) {
    scrollArea.value.setScrollPosition('vertical', 999999, 300)
  }
}
</script>

<style scoped>
.chat-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.welcome-card {
  max-width: 600px;
  margin: 0 auto;
}

.example-btn {
  font-size: 0.8rem;
  padding: 8px 12px;
}

.message-wrapper {
  max-width: 100%;
}

.ai-message {
  line-height: 1.6;
}

.ai-message :deep(h1),
.ai-message :deep(h2),
.ai-message :deep(h3) {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: 600;
}

.ai-message :deep(ul),
.ai-message :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.ai-message :deep(li) {
  margin: 0.25em 0;
}

.ai-message :deep(p) {
  margin: 0.5em 0;
}

.ai-message :deep(strong) {
  font-weight: 600;
}

.message-actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
  margin-right: 20px;
}

.input-container {
  background: white;
}

.typing-indicator {
  display: flex;
  align-items: center;
  color: #666;
  font-style: italic;
}

.disclaimer {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

@media (max-width: 600px) {
  .example-btn {
    font-size: 0.7rem;
    padding: 6px 10px;
  }
  
  .welcome-card .q-pa-xl {
    padding: 24px 16px;
  }
}
</style>
