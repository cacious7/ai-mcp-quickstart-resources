<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero q-pa-xl">
      <div class="row items-center q-gutter-xl">
        <div class="col-md-6 col-12">
          <div class="hero-content">
            <q-badge color="primary" class="text-h6 q-pa-sm q-mb-md">
              AI-Powered Legal Assistant
            </q-badge>
            <h1 class="hero-title text-h2 text-weight-bold q-mb-md">
              Zambian Legal AI Assistant
            </h1>
            <p class="hero-subtitle text-h6 text-grey-7 q-mb-xl">
              Get simplified explanations of Zambian laws in natural language. 
              Understanding your legal rights has never been easier.
            </p>
            <div class="hero-actions row q-gutter-md">
              <q-btn
                @click="navigateToChat('')"
                color="primary"
                size="lg"
                class="q-px-xl q-py-md"
                no-caps
                icon="chat"
              >
                <span class="q-ml-sm">Ask Legal Questions</span>
              </q-btn>
              <q-btn
                to="/laws"
                color="secondary"
                size="lg"
                outline
                class="q-px-xl q-py-md"
                no-caps
                icon="menu_book"
              >
                <span class="q-ml-sm">Browse Laws</span>
              </q-btn>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 col-12 text-center">
          <q-icon 
            name="account_balance" 
            size="300px" 
            color="primary" 
            class="hero-icon"
          />
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features q-pa-xl bg-grey-1">
      <div class="text-center q-mb-xl">
        <h2 class="text-h3 text-weight-bold q-mb-md">How It Works</h2>
        <p class="text-h6 text-grey-7">Simple, accessible legal information at your fingertips</p>
      </div>
      
      <div class="row q-gutter-lg justify-center">
        <div v-for="feature in features" :key="feature.title" class="col-md-3 col-sm-6 col-12">
          <q-card class="feature-card h-full">
            <q-card-section class="text-center q-pa-xl">
              <q-icon :name="feature.icon" size="64px" :color="feature.color" class="q-mb-md" />
              <h3 class="text-h5 q-mb-md">{{ feature.title }}</h3>
              <p class="text-grey-7">{{ feature.description }}</p>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Popular Topics Section -->
    <section class="popular-topics q-pa-xl">
      <div class="text-center q-mb-xl">
        <h2 class="text-h3 text-weight-bold q-mb-md">Popular Legal Topics</h2>
        <p class="text-h6 text-grey-7">Quick access to commonly asked questions</p>
      </div>
      
      <div class="row q-gutter-md justify-center">
        <div v-for="topic in popularTopics" :key="topic.title" class="col-auto">
          <q-btn
            @click="navigateToChat(topic.query)"
            :color="topic.color"
            size="lg"
            outline
            class="topic-btn q-pa-md"
            no-caps
          >
            <div class="column items-center">
              <q-icon :name="topic.icon" size="32px" class="q-mb-sm" />
              <span>{{ topic.title }}</span>
            </div>
          </q-btn>
        </div>
      </div>
    </section>

    <!-- Example Questions Section -->
    <section class="example-questions q-pa-xl bg-grey-1">
      <div class="text-center q-mb-xl">
        <h2 class="text-h3 text-weight-bold q-mb-md">Try These Questions</h2>
        <p class="text-h6 text-grey-7">See how our AI can help with real legal scenarios</p>
      </div>
      
      <div class="row q-gutter-md justify-center">
        <div v-for="question in exampleQuestions" :key="question" class="col-md-4 col-12">
          <q-card 
            class="example-card cursor-pointer"
            @click="navigateToChat(question)"
            flat
            bordered
          >
            <q-card-section class="q-pa-lg">
              <q-icon name="help_outline" color="primary" size="24px" class="q-mb-md" />
              <p class="text-body1">"{{ question }}"</p>
              <q-btn
                color="primary"
                flat
                size="sm"
                icon="arrow_forward"
                label="Ask this question"
                class="q-mt-md"
              />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Quick Search Section -->
    <section class="quick-search q-pa-xl">
      <div class="row justify-center">
        <div class="col-md-8 col-12">
          <q-card class="search-card">
            <q-card-section class="q-pa-xl text-center">
              <h3 class="text-h4 q-mb-md">Have a Legal Question?</h3>
              <p class="text-h6 text-grey-7 q-mb-lg">
                Ask in plain language and get simplified explanations
              </p>
              
              <q-form @submit="navigateToChat(searchQuery)" class="search-form">
                <div class="row q-gutter-md items-end">
                  <div class="col">
                    <q-input
                      v-model="searchQuery"
                      placeholder="e.g., What are my rights as a tenant in Zambia?"
                      outlined
                      dense
                      class="search-input"
                    >
                      <template v-slot:prepend>
                        <q-icon name="search" />
                      </template>
                    </q-input>
                  </div>
                  <div class="col-auto">
                    <q-btn
                      type="submit"
                      color="primary"
                      size="lg"
                      icon="send"
                      :disable="!searchQuery.trim()"
                      class="q-px-xl"
                    >
                      Ask AI
                    </q-btn>
                  </div>
                </div>
              </q-form>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Important Notice -->
    <section class="disclaimer q-pa-xl bg-warning-1">
      <div class="row justify-center">
        <div class="col-md-10 col-12">
          <q-banner class="bg-warning text-dark" rounded>
            <template v-slot:avatar>
              <q-icon name="info" color="warning" />
            </template>
            <div class="text-h6 q-mb-sm">Important Legal Disclaimer</div>
            <p class="text-body1">
              This AI assistant provides general information about Zambian law for educational purposes only. 
              It does not constitute legal advice and should not be relied upon for specific legal matters. 
              Always consult with qualified legal professionals for personalized legal guidance.
            </p>
            <template v-slot:action>
              <q-btn 
                flat 
                color="warning" 
                label="Learn More" 
                to="/disclaimer" 
              />
            </template>
          </q-banner>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

const features = [
  {
    icon: 'chat',
    color: 'primary',
    title: 'Natural Language',
    description: 'Ask questions in plain English and get clear, understandable answers about Zambian law.'
  },
  {
    icon: 'verified',
    color: 'positive',
    title: 'Accurate Information',
    description: 'Responses are based on current Zambian legal frameworks and regulations.'
  },
  {
    icon: 'speed',
    color: 'accent',
    title: 'Instant Answers',
    description: 'Get immediate responses to your legal questions, available 24/7.'
  },
  {
    icon: 'accessibility',
    color: 'secondary',
    title: 'Accessible',
    description: 'Legal information simplified for everyone, regardless of legal background.'
  }
]

const popularTopics = [
  {
    title: 'Employment',
    icon: 'work',
    color: 'primary',
    query: 'What are my employment rights in Zambia?'
  },
  {
    title: 'Family Law',
    icon: 'family_restroom',
    color: 'secondary',
    query: 'What are the marriage laws in Zambia?'
  },
  {
    title: 'Property',
    icon: 'home',
    color: 'accent',
    query: 'How do property ownership laws work in Zambia?'
  },
  {
    title: 'Criminal Law',
    icon: 'gavel',
    color: 'negative',
    query: 'What should I know about criminal procedure in Zambia?'
  },
  {
    title: 'Business',
    icon: 'business',
    color: 'positive',
    query: 'How do I start a business legally in Zambia?'
  },
  {
    title: 'Civil Rights',
    icon: 'balance',
    color: 'info',
    query: 'What are my constitutional rights in Zambia?'
  }
]

const exampleQuestions = [
  'What are the legal requirements for getting married in Zambia?',
  'Can my employer fire me without notice?',
  'What should I do if I\'m arrested in Zambia?',
  'How do I legally buy property as a foreigner?',
  'What are my rights as a tenant?',
  'How do I start a small business legally?'
]

const navigateToChat = (initialQuery: string) => {
  if (initialQuery.trim()) {
    router.push({ path: '/chat', query: { q: initialQuery } })
  } else {
    router.push('/chat')
  }
  searchQuery.value = ''
}
</script>

<style scoped>
.home-view {
  min-height: 100vh;
}

.hero {
  min-height: 80vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.hero-icon {
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.feature-card {
  height: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.topic-btn {
  min-width: 120px;
  min-height: 100px;
  transition: transform 0.2s ease;
}

.topic-btn:hover {
  transform: scale(1.05);
}

.example-card {
  height: 100%;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.example-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.search-card {
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.search-input {
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .hero {
    min-height: 60vh;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .topic-btn {
    min-width: 100px;
    min-height: 80px;
  }
}
</style>
