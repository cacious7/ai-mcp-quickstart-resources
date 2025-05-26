import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface LegalDocument {
  id: string
  title: string
  description: string
  category: string
  type: 'act' | 'regulation' | 'statutory' | 'constitution' | 'case-law'
  typeLabel: string
  year: number
  chapters?: number
  sections?: number
  content?: string
  url?: string
  tags: string[]
  lastUpdated: Date
  isPopular?: boolean
}

export interface LegalCategory {
  id: string
  name: string
  description: string
  count: number
  icon?: string
  subcategories?: LegalSubcategory[]
}

export interface LegalSubcategory {
  id: string
  name: string
  count: number
}

export interface LegalUpdate {
  id: string
  title: string
  description: string
  date: Date
  type: 'amendment' | 'new-law' | 'repeal' | 'case-law'
  affectedLaws: string[]
  importance: 'high' | 'medium' | 'low'
}

export interface SearchFilters {
  query: string
  category: string
  type: string
  year: string
  tags: string[]
}

export const useLegalDataStore = defineStore('legalData', () => {
  // State
  const documents = ref<LegalDocument[]>([])
  const categories = ref<LegalCategory[]>([])
  const updates = ref<LegalUpdate[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchFilters = ref<SearchFilters>({
    query: '',
    category: '',
    type: '',
    year: '',
    tags: []
  })

  // Getters
  const filteredDocuments = computed(() => {
    let filtered = documents.value

    if (searchFilters.value.query) {
      const query = searchFilters.value.query.toLowerCase()
      filtered = filtered.filter(doc =>
        doc.title.toLowerCase().includes(query) ||
        doc.description.toLowerCase().includes(query) ||
        doc.tags.some(tag => tag.toLowerCase().includes(query))
      )
    }

    if (searchFilters.value.category) {
      filtered = filtered.filter(doc => doc.category === searchFilters.value.category)
    }

    if (searchFilters.value.type) {
      filtered = filtered.filter(doc => doc.type === searchFilters.value.type)
    }

    if (searchFilters.value.year) {
      filtered = filtered.filter(doc => doc.year.toString() === searchFilters.value.year)
    }

    if (searchFilters.value.tags.length > 0) {
      filtered = filtered.filter(doc =>
        searchFilters.value.tags.some(tag => doc.tags.includes(tag))
      )
    }

    return filtered
  })

  const popularDocuments = computed(() => {
    return documents.value.filter(doc => doc.isPopular).slice(0, 10)
  })

  const recentDocuments = computed(() => {
    return documents.value
      .slice()
      .sort((a, b) => b.lastUpdated.getTime() - a.lastUpdated.getTime())
      .slice(0, 10)
  })

  const documentsByCategory = computed(() => {
    const grouped: { [key: string]: LegalDocument[] } = {}
    documents.value.forEach(doc => {
      if (!grouped[doc.category]) {
        grouped[doc.category] = []
      }
      grouped[doc.category].push(doc)
    })
    return grouped
  })

  const availableYears = computed(() => {
    const years = [...new Set(documents.value.map(doc => doc.year))]
    return years.sort((a, b) => b - a)
  })

  const availableTags = computed(() => {
    const tags = new Set<string>()
    documents.value.forEach(doc => {
      doc.tags.forEach(tag => tags.add(tag))
    })
    return Array.from(tags).sort()
  })

  const recentUpdates = computed(() => {
    return updates.value
      .slice()
      .sort((a, b) => b.date.getTime() - a.date.getTime())
      .slice(0, 5)
  })

  const importantUpdates = computed(() => {
    return updates.value.filter(update => update.importance === 'high')
  })

  // Actions
  const initializeData = async () => {
    // If already loaded, don't reload
    if (documents.value.length > 0) {
      return
    }
    
    loading.value = true
    error.value = null

    try {
      await Promise.all([
        loadDocuments(),
        loadCategories(),
        loadUpdates()
      ])
    } catch (err) {
      console.error('Error loading legal data:', err)
      error.value = err instanceof Error ? err.message : 'Failed to load legal data'
    } finally {
      loading.value = false
    }
  }

  const loadDocuments = async () => {
    // Mock data - in real app this would come from API
    documents.value = [
      {
        id: '1',
        title: 'The Constitution of Zambia',
        description: 'The supreme law of the Republic of Zambia, establishing the framework of government and fundamental rights.',
        category: 'Constitutional Law',
        type: 'constitution',
        typeLabel: 'Constitution',
        year: 2016,
        chapters: 23,
        sections: 266,
        tags: ['constitution', 'fundamental-rights', 'government', 'democracy'],
        lastUpdated: new Date('2023-12-01'),
        isPopular: true
      },
      {
        id: '2',
        title: 'The Penal Code Act',
        description: 'Defines criminal offenses and their punishments under Zambian law.',
        category: 'Criminal Law',
        type: 'act',
        typeLabel: 'Act',
        year: 1930,
        chapters: 45,
        sections: 384,
        tags: ['criminal-law', 'offenses', 'punishment', 'crimes'],
        lastUpdated: new Date('2023-11-15'),
        isPopular: true
      },
      {
        id: '3',
        title: 'The Companies Act No. 10 of 2017',
        description: 'Governs the formation, management, and dissolution of companies in Zambia.',
        category: 'Business & Commercial',
        type: 'act',
        typeLabel: 'Act',
        year: 2017,
        chapters: 35,
        sections: 512,
        tags: ['companies', 'business', 'corporate-law', 'registration'],
        lastUpdated: new Date('2024-01-10'),
        isPopular: true
      },
      {
        id: '4',
        title: 'The Employment Act No. 3 of 2019',
        description: 'Regulates employment relationships and workers\' rights in Zambia.',
        category: 'Employment Law',
        type: 'act',
        typeLabel: 'Act',
        year: 2019,
        chapters: 12,
        sections: 156,
        tags: ['employment', 'workers-rights', 'labor-relations', 'workplace'],
        lastUpdated: new Date('2023-10-20'),
        isPopular: true
      },
      {
        id: '5',
        title: 'The Lands Act No. 29 of 1995',
        description: 'Governs land ownership, acquisition, and use in Zambia.',
        category: 'Property Law',
        type: 'act',
        typeLabel: 'Act',
        year: 1995,
        chapters: 8,
        sections: 94,
        tags: ['land', 'property', 'ownership', 'real-estate'],
        lastUpdated: new Date('2023-09-05'),
        isPopular: false
      }
    ]
  }

  const loadCategories = async () => {
    categories.value = [
      {
        id: 'constitutional',
        name: 'Constitutional Law',
        description: 'Laws relating to the constitution and government structure',
        count: 15,
        subcategories: [
          { id: 'fundamental-rights', name: 'Fundamental Rights', count: 8 },
          { id: 'government-structure', name: 'Government Structure', count: 7 }
        ]
      },
      {
        id: 'criminal',
        name: 'Criminal Law',
        description: 'Laws defining crimes and criminal procedures',
        count: 45,
        subcategories: [
          { id: 'offenses', name: 'Criminal Offenses', count: 25 },
          { id: 'procedure', name: 'Criminal Procedure', count: 20 }
        ]
      },
      {
        id: 'civil',
        name: 'Civil Law',
        description: 'Laws governing civil disputes and procedures',
        count: 38,
        subcategories: [
          { id: 'contracts', name: 'Contracts', count: 18 },
          { id: 'civil-procedure', name: 'Civil Procedure', count: 20 }
        ]
      },
      {
        id: 'business',
        name: 'Business & Commercial',
        description: 'Laws regulating business activities and commerce',
        count: 52,
        subcategories: [
          { id: 'company-law', name: 'Company Law', count: 25 },
          { id: 'commercial-transactions', name: 'Commercial Transactions', count: 27 }
        ]
      },
      {
        id: 'family',
        name: 'Family Law',
        description: 'Laws relating to marriage, divorce, and family matters',
        count: 23,
        subcategories: [
          { id: 'marriage', name: 'Marriage & Divorce', count: 15 },
          { id: 'children', name: 'Children & Custody', count: 8 }
        ]
      },
      {
        id: 'employment',
        name: 'Employment Law',
        description: 'Laws governing employment relationships and worker rights',
        count: 31,
        subcategories: [
          { id: 'labor-relations', name: 'Labor Relations', count: 18 },
          { id: 'workers-compensation', name: 'Workers\' Compensation', count: 13 }
        ]
      },
      {
        id: 'property',
        name: 'Property Law',
        description: 'Laws relating to land ownership and real estate',
        count: 29,
        subcategories: [
          { id: 'land-ownership', name: 'Land Ownership', count: 15 },
          { id: 'real-estate-transactions', name: 'Real Estate Transactions', count: 14 }
        ]
      },
      {
        id: 'tax',
        name: 'Tax Law',
        description: 'Laws governing taxation and revenue collection',
        count: 18,
        subcategories: [
          { id: 'income-tax', name: 'Income Tax', count: 10 },
          { id: 'vat', name: 'Value Added Tax', count: 8 }
        ]
      }
    ]
  }

  const loadUpdates = async () => {
    updates.value = [
      {
        id: '1',
        title: 'Amendment to Companies Act 2017',
        description: 'New provisions for digital company registration and electronic signatures in corporate documents.',
        date: new Date('2024-01-15'),
        type: 'amendment',
        affectedLaws: ['companies-act-2017'],
        importance: 'high'
      },
      {
        id: '2',
        title: 'Criminal Procedure Code Updates',
        description: 'Enhanced provisions for witness protection and admissibility of digital evidence.',
        date: new Date('2024-01-10'),
        type: 'amendment',
        affectedLaws: ['criminal-procedure-code'],
        importance: 'medium'
      },
      {
        id: '3',
        title: 'New Employment Regulations',
        description: 'Updated regulations on remote work arrangements and digital employment contracts.',
        date: new Date('2023-12-20'),
        type: 'new-law',
        affectedLaws: ['employment-act-2019'],
        importance: 'medium'
      }
    ]
  }

  const searchDocuments = (query: string) => {
    searchFilters.value.query = query
  }

  const setFilter = (filterType: keyof SearchFilters, value: string | string[]) => {
    ;(searchFilters.value as any)[filterType] = value
  }

  const clearFilters = () => {
    searchFilters.value = {
      query: '',
      category: '',
      type: '',
      year: '',
      tags: []
    }
  }

  const getDocumentById = (id: string): LegalDocument | undefined => {
    return documents.value.find(doc => doc.id === id)
  }

  const getDocumentsByCategory = (categoryId: string): LegalDocument[] => {
    const category = categories.value.find(cat => cat.id === categoryId)
    if (!category) return []
    
    return documents.value.filter(doc => doc.category === category.name)
  }

  const getCategoryById = (id: string): LegalCategory | undefined => {
    return categories.value.find(cat => cat.id === id)
  }

  const addToFavorites = (documentId: string) => {
    // Implementation for favorites functionality
    const favorites = getFavorites()
    if (!favorites.includes(documentId)) {
      favorites.push(documentId)
      saveFavorites(favorites)
    }
  }

  const removeFromFavorites = (documentId: string) => {
    const favorites = getFavorites()
    const index = favorites.indexOf(documentId)
    if (index > -1) {
      favorites.splice(index, 1)
      saveFavorites(favorites)
    }
  }

  const isFavorite = (documentId: string): boolean => {
    return getFavorites().includes(documentId)
  }

  const getFavorites = (): string[] => {
    try {
      const stored = localStorage.getItem('legal-favorites')
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  }

  const saveFavorites = (favorites: string[]) => {
    try {
      localStorage.setItem('legal-favorites', JSON.stringify(favorites))
    } catch (error) {
      console.error('Failed to save favorites:', error)
    }
  }

  const getFavoriteDocuments = computed(() => {
    const favoriteIds = getFavorites()
    return documents.value.filter(doc => favoriteIds.includes(doc.id))
  })

  // Statistics
  const getStatistics = computed(() => {
    return {
      totalDocuments: documents.value.length,
      totalCategories: categories.value.length,
      recentUpdates: updates.value.filter(update => {
        const weekAgo = new Date()
        weekAgo.setDate(weekAgo.getDate() - 7)
        return update.date >= weekAgo
      }).length,
      popularDocuments: popularDocuments.value.length
    }
  })

  return {
    // State
    documents,
    categories,
    updates,
    loading,
    error,
    searchFilters,

    // Getters
    filteredDocuments,
    popularDocuments,
    recentDocuments,
    documentsByCategory,
    availableYears,
    availableTags,
    recentUpdates,
    importantUpdates,
    getFavoriteDocuments,
    getStatistics,

    // Actions
    initializeData,
    searchDocuments,
    setFilter,
    clearFilters,
    getDocumentById,
    getDocumentsByCategory,
    getCategoryById,
    addToFavorites,
    removeFromFavorites,
    isFavorite
  }
})
