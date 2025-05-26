<template>
  <div class="laws-page">
    <!-- Header Section -->
    <section class="laws-header bg-primary text-white">
      <div class="container">
        <div class="header-content">
          <h1 class="page-title">Zambian Laws & Regulations</h1>
          <p class="subtitle">
            Explore comprehensive legal information organized by categories and topics
          </p>
          
          <!-- Search Bar -->
          <div class="search-section">
            <div class="search-bar">
              <SearchIcon class="search-icon" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search laws, acts, regulations..."
                class="search-input"
                @keyup.enter="performSearch"
              />
              <button @click="performSearch" class="search-btn">
                Search
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Filter Section -->
    <section class="filter-section bg-gray-50">
      <div class="container">
        <div class="filters">
          <div class="filter-group">
            <label for="category">Category:</label>
            <select id="category" v-model="selectedCategory" @change="filterLaws">
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="type">Type:</label>
            <select id="type" v-model="selectedType" @change="filterLaws">
              <option value="">All Types</option>
              <option value="act">Acts</option>
              <option value="regulation">Regulations</option>
              <option value="statutory">Statutory Instruments</option>
              <option value="constitution">Constitution</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="year">Year:</label>
            <select id="year" v-model="selectedYear" @change="filterLaws">
              <option value="">All Years</option>
              <option v-for="year in availableYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>
          
          <button @click="clearFilters" class="clear-filters-btn">
            <ClearIcon />
            Clear Filters
          </button>
        </div>
      </div>
    </section>

    <!-- Quick Access Categories -->
    <section class="section">
      <div class="container">
        <h2 class="section-title">Popular Legal Categories</h2>
        <div class="categories-grid">
          <div
            v-for="category in popularCategories"
            :key="category.id"
            class="category-card"
            @click="selectCategory(category.id)"
          >
            <div class="category-icon">
              <component :is="category.icon" />
            </div>
            <h3>{{ category.name }}</h3>
            <p>{{ category.description }}</p>
            <span class="laws-count">{{ category.count }} laws</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Laws List -->
    <section class="section bg-gray-50">
      <div class="container">
        <div class="laws-header-row">
          <h2 class="section-title">
            {{ filteredTitle }}
            <span v-if="filteredLaws.length > 0" class="results-count">
              ({{ filteredLaws.length }} {{ filteredLaws.length === 1 ? 'result' : 'results' }})
            </span>
          </h2>
          
          <div class="view-controls">
            <button
              @click="viewMode = 'grid'"
              :class="['view-btn', { active: viewMode === 'grid' }]"
            >
              <GridIcon />
              Grid
            </button>
            <button
              @click="viewMode = 'list'"
              :class="['view-btn', { active: viewMode === 'list' }]"
            >
              <ListIcon />
              List
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <LoadingIcon class="loading-icon" />
          <p>Loading legal information...</p>
        </div>

        <!-- No Results -->
        <div v-else-if="filteredLaws.length === 0" class="no-results">
          <NoResultsIcon class="no-results-icon" />
          <h3>No laws found</h3>
          <p>Try adjusting your search criteria or filters.</p>
          <button @click="clearFilters" class="btn btn-primary">
            Clear All Filters
          </button>
        </div>

        <!-- Laws Grid/List -->
        <div v-else :class="['laws-container', viewMode]">
          <div
            v-for="law in paginatedLaws"
            :key="law.id"
            class="law-card"
            @click="openLaw(law)"
          >
            <div class="law-header">
              <div class="law-type-badge" :class="law.type">
                {{ law.typeLabel }}
              </div>
              <div class="law-year">{{ law.year }}</div>
            </div>
            
            <h3 class="law-title">{{ law.title }}</h3>
            <p class="law-description">{{ law.description }}</p>
            
            <div class="law-meta">
              <div class="law-category">
                <CategoryIcon />
                {{ law.category }}
              </div>
              <div class="law-chapters" v-if="law.chapters">
                <ChaptersIcon />
                {{ law.chapters }} chapters
              </div>
            </div>
            
            <div class="law-actions">
              <button @click.stop="viewLaw(law)" class="btn btn-sm btn-outline">
                <ViewIcon />
                View
              </button>
              <button @click.stop="askAboutLaw(law)" class="btn btn-sm btn-primary">
                <ChatIcon />
                Ask AI
              </button>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="pagination-btn"
          >
            <PrevIcon />
            Previous
          </button>
          
          <div class="pagination-info">
            <span>Page {{ currentPage }} of {{ totalPages }}</span>
          </div>
          
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="pagination-btn"
          >
            Next
            <NextIcon />
          </button>
        </div>
      </div>
    </section>

    <!-- Recent Updates -->
    <section class="section">
      <div class="container">
        <h2 class="section-title">Recent Legal Updates</h2>
        <div class="updates-list">
          <div v-for="update in recentUpdates" :key="update.id" class="update-item">
            <div class="update-date">
              <CalendarIcon />
              {{ formatDate(update.date) }}
            </div>
            <div class="update-content">
              <h4>{{ update.title }}</h4>
              <p>{{ update.description }}</p>
              <button @click="viewUpdate(update)" class="update-link">
                Read More <ArrowIcon />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Help Section -->
    <section class="section bg-primary text-white">
      <div class="container">
        <div class="help-section text-center">
          <HelpIcon class="help-icon" />
          <h2>Need Help Finding Specific Legal Information?</h2>
          <p class="help-text">
            Our AI assistant can help you find relevant laws and provide explanations
            in simple language. Try asking specific questions about Zambian law.
          </p>
          <router-link to="/chat" class="btn btn-white">
            <ChatIcon />
            Chat with AI Assistant
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLegalDataStore } from '@/stores'

// Import icon components
import SearchIcon from '@/components/icons/SearchIcon.vue'
import ClearIcon from '@/components/icons/ClearIcon.vue'
import GridIcon from '@/components/icons/GridIcon.vue'
import ListIcon from '@/components/icons/ListIcon.vue'
import LoadingIcon from '@/components/icons/LoadingIcon.vue'
import NoResultsIcon from '@/components/icons/NoResultsIcon.vue'
import CategoryIcon from '@/components/icons/CategoryIcon.vue'
import ChaptersIcon from '@/components/icons/ChaptersIcon.vue'
import ViewIcon from '@/components/icons/ViewIcon.vue'
import ChatIcon from '@/components/icons/ChatIcon.vue'
import PrevIcon from '@/components/icons/PrevIcon.vue'
import NextIcon from '@/components/icons/NextIcon.vue'
import CalendarIcon from '@/components/icons/CalendarIcon.vue'
import ArrowIcon from '@/components/icons/ArrowIcon.vue'
import HelpIcon from '@/components/icons/HelpIcon.vue'

// Category icons
import CriminalIcon from '@/components/icons/CriminalIcon.vue'
import CivilIcon from '@/components/icons/CivilIcon.vue'
import BusinessIcon from '@/components/icons/BusinessIcon.vue'
import FamilyIcon from '@/components/icons/FamilyIcon.vue'
import EmploymentIcon from '@/components/icons/EmploymentIcon.vue'
import PropertyIcon from '@/components/icons/PropertyIcon.vue'

// TODO: Add SEO meta tags when @vueuse/head is available

const router = useRouter()

// Reactive data
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedType = ref('')
const selectedYear = ref('')
const viewMode = ref<'grid' | 'list'>('grid')
const currentPage = ref(1)
const itemsPerPage = 12

// Remove mock data, initialize and use real data from the store
const legalStore = useLegalDataStore()
onMounted(() => {
  // Load laws data and handle loading state
  loading.value = true;
  legalStore.initializeData().then(() => {
    // Give a small delay to ensure store is updated
    setTimeout(() => {
      loading.value = false;
    }, 300);
  }).catch(err => {
    console.error('Error initializing legal data:', err);
    loading.value = false;
  });
})

const categories = computed(() => legalStore.categories)
const documents = computed(() => legalStore.filteredDocuments)

const popularCategories = ref([
  {
    id: 'criminal',
    name: 'Criminal Law',
    description: 'Penal code, criminal procedures, and offenses',
    count: 45,
    icon: CriminalIcon
  },
  {
    id: 'civil',
    name: 'Civil Law',
    description: 'Civil procedures, contracts, and disputes',
    count: 38,
    icon: CivilIcon
  },
  {
    id: 'business',
    name: 'Business Law',
    description: 'Company law, commercial transactions',
    count: 52,
    icon: BusinessIcon
  },
  {
    id: 'family',
    name: 'Family Law',
    description: 'Marriage, divorce, child custody',
    count: 23,
    icon: FamilyIcon
  },
  {
    id: 'employment',
    name: 'Employment',
    description: 'Labor relations, worker rights',
    count: 31,
    icon: EmploymentIcon
  },
  {
    id: 'property',
    name: 'Property Law',
    description: 'Land ownership, real estate',
    count: 29,
    icon: PropertyIcon
  }
])

// Bind loading to store's loading state
const loading = computed(() => legalStore.loading)

// Use store's recentUpdates
const recentUpdates = computed(() => legalStore.recentUpdates)

// Computed properties
const availableYears = computed(() => {
  const years = [...new Set(documents.value.map(law => law.year))].sort((a, b) => b - a)
  return years
})

const filteredLaws = computed(() => {
  let laws = documents.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    laws = laws.filter(law =>
      law.title.toLowerCase().includes(query) ||
      law.description.toLowerCase().includes(query) ||
      law.category.toLowerCase().includes(query)
    )
  }

  if (selectedCategory.value) {
    const categoryName = categories.value.find(c => c.id === selectedCategory.value)?.name
    laws = laws.filter(law => law.category === categoryName)
  }

  if (selectedType.value) {
    laws = laws.filter(law => law.type === selectedType.value)
  }

  if (selectedYear.value) {
    laws = laws.filter(law => law.year === parseInt(selectedYear.value))
  }

  return laws
})

const filteredTitle = computed(() => {
  if (searchQuery.value) {
    return `Search Results for "${searchQuery.value}"`
  }
  if (selectedCategory.value) {
    const categoryName = categories.value.find(c => c.id === selectedCategory.value)?.name
    return `${categoryName} Laws`
  }
  return 'All Laws & Regulations'
})

const totalPages = computed(() => {
  return Math.ceil(filteredLaws.value.length / itemsPerPage)
})

const paginatedLaws = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredLaws.value.slice(start, end)
})

// Methods
const performSearch = () => {
  currentPage.value = 1
  legalStore.searchDocuments(searchQuery.value)
}

const filterLaws = () => {
  currentPage.value = 1
  legalStore.setFilter('category', selectedCategory.value)
  legalStore.setFilter('type', selectedType.value)
  legalStore.setFilter('year', selectedYear.value)
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedType.value = ''
  selectedYear.value = ''
  currentPage.value = 1
  legalStore.clearFilters()
}

const selectCategory = (categoryId: string) => {
  selectedCategory.value = categoryId
  filterLaws()
}

const goToPage = (page: number) => {
  currentPage.value = page
  // Scroll to top of laws section
  document.querySelector('.laws-container')?.scrollIntoView({ behavior: 'smooth' })
}

const openLaw = (law: any) => {
  // In real app, this would navigate to law detail page
  console.log('Opening law:', law.title)
}

const viewLaw = (law: any) => {
  // Navigate to law detail view
  console.log('Viewing law:', law.title)
}

const askAboutLaw = (law: any) => {
  // Navigate to chat with pre-filled question about this law
  router.push({
    path: '/chat',
    query: { topic: law.title }
  })
}

const viewUpdate = (update: any) => {
  console.log('Viewing update:', update.title)
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  // Load laws data and handle loading state
  loading.value = true;
  legalStore.initializeData().then(() => {
    // Give a small delay to ensure store is updated
    setTimeout(() => {
      loading.value = false;
    }, 300);
  }).catch(err => {
    console.error('Error initializing legal data:', err);
    loading.value = false;
  });
})
</script>

<style scoped>
.laws-page {
  min-height: 100vh;
}

.laws-header {
  padding: 3rem 0;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
}

.header-content {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.search-section {
  margin-top: 2rem;
}

.search-bar {
  display: flex;
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.search-icon {
  padding: 1rem;
  color: var(--color-gray-500);
  background: white;
}

.search-input {
  flex: 1;
  padding: 1rem 0;
  border: none;
  outline: none;
  font-size: 1rem;
}

.search-btn {
  padding: 1rem 1.5rem;
  background: var(--color-secondary);
  color: white;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-btn:hover {
  background: var(--color-secondary-dark);
}

.filter-section {
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--color-gray-200);
}

.filters {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: var(--color-gray-700);
  white-space: nowrap;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid var(--color-gray-300);
  border-radius: var(--border-radius-sm);
  background: white;
  min-width: 120px;
}

.clear-filters-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-gray-100);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-filters-btn:hover {
  background: var(--color-gray-200);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.category-card {
  background: white;
  padding: 2rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.category-icon {
  width: 3rem;
  height: 3rem;
  background: var(--color-primary-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: var(--color-primary);
}

.laws-count {
  display: inline-block;
  background: var(--color-gray-100);
  color: var(--color-gray-600);
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-full);
  font-size: 0.875rem;
  margin-top: 1rem;
}

.laws-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.results-count {
  color: var(--color-gray-600);
  font-weight: normal;
  font-size: 1rem;
}

.view-controls {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-gray-300);
  background: white;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.loading-state,
.no-results {
  text-align: center;
  padding: 3rem 0;
}

.loading-icon,
.no-results-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
  color: var(--color-gray-500);
}

.laws-container.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.laws-container.list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.law-card {
  background: white;
  border: 1px solid var(--color-gray-200);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.law-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.laws-container.list .law-card {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.law-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.law-type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-full);
  font-size: 0.875rem;
  font-weight: 500;
}

.law-type-badge.act {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.law-type-badge.regulation {
  background: var(--color-secondary-light);
  color: var(--color-secondary-dark);
}

.law-type-badge.constitution {
  background: var(--color-success-light);
  color: var(--color-success-dark);
}

.law-year {
  color: var(--color-gray-600);
  font-weight: 500;
}

.law-title {
  margin-bottom: 0.75rem;
  color: var(--color-primary);
}

.law-description {
  color: var(--color-gray-600);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.law-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

.law-category,
.law-chapters {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.law-actions {
  display: flex;
  gap: 0.75rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 3rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-gray-300);
  background: white;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-gray-50);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: var(--color-gray-600);
  font-weight: 500;
}

.updates-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.update-item {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--color-gray-200);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
}

.update-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-gray-600);
  font-size: 0.875rem;
  white-space: nowrap;
}

.update-content h4 {
  margin-bottom: 0.5rem;
  color: var(--color-primary);
}

.update-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--color-primary);
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  margin-top: 0.5rem;
}

.help-section {
  text-align: center;
  padding: 3rem 0;
}

.help-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
  opacity: 0.9;
}

.help-text {
  font-size: 1.125rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn-white {
  background: white;
  color: var(--color-primary);
}

.btn-white:hover {
  background: var(--color-gray-100);
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .search-bar {
    flex-direction: column;
  }

  .search-input {
    padding: 1rem;
  }

  .filters {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group select {
    min-width: auto;
  }

  .laws-header-row {
    flex-direction: column;
    align-items: stretch;
  }

  .laws-container.grid {
    grid-template-columns: 1fr;
  }

  .laws-container.list .law-card {
    flex-direction: column;
  }

  .update-item {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
