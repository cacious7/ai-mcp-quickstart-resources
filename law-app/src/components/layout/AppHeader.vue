<template>
  <header class="app-header">
    <div class="container">
      <div class="header-content">        <RouterLink to="/" class="logo">
          <img src="/favicon.svg" alt="Legal AI" class="logo-icon">
          <span class="logo-text">Legal AI</span>
        </RouterLink>
        
        <nav class="main-nav" :class="{ active: isMenuOpen }">
          <RouterLink to="/" class="nav-link" @click="closeMenu">Home</RouterLink>
          <RouterLink to="/chat" class="nav-link" @click="closeMenu">Ask AI</RouterLink>
          <RouterLink to="/laws" class="nav-link" @click="closeMenu">Browse Laws</RouterLink>
          <RouterLink to="/about" class="nav-link" @click="closeMenu">About</RouterLink>
        </nav>
        
        <button 
          class="menu-toggle"
          @click="toggleMenu"
          :aria-expanded="isMenuOpen"
          aria-label="Toggle navigation menu"
        >
          <span class="hamburger"></span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}
</script>

<style scoped>
.app-header {
  background-color: var(--primary);
  color: white;
  box-shadow: var(--shadow-md);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: white;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 600;
}

.logo:hover {
  color: white;
  text-decoration: none;
}

.logo-icon {
  width: 32px;
  height: 32px;
}

.logo-text {
  white-space: nowrap;
}

.main-nav {
  display: flex;
  gap: var(--space-lg);
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  text-decoration: none;
}

.nav-link.router-link-active {
  background-color: var(--primary-dark);
  color: white;
}

.menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-sm);
}

.hamburger {
  width: 24px;
  height: 2px;
  background-color: white;
  transition: all var(--transition-fast);
  position: relative;
}

.hamburger::before,
.hamburger::after {
  content: '';
  position: absolute;
  width: 24px;
  height: 2px;
  background-color: white;
  transition: all var(--transition-fast);
}

.hamburger::before {
  top: -8px;
}

.hamburger::after {
  top: 8px;
}

/* Mobile styles */
@media (max-width: 768px) {
  .menu-toggle {
    display: flex;
  }
  
  .main-nav {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: var(--primary);
    flex-direction: column;
    padding: var(--space-md);
    box-shadow: var(--shadow-md);
    transform: translateY(-100%);
    opacity: 0;
    visibility: hidden;
    transition: all var(--transition-normal);
  }
  
  .main-nav.active {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }
  
  .nav-link {
    width: 100%;
    text-align: center;
    padding: var(--space-md);
  }
  
  /* Animate hamburger */
  .menu-toggle[aria-expanded="true"] .hamburger {
    background-color: transparent;
  }
  
  .menu-toggle[aria-expanded="true"] .hamburger::before {
    transform: rotate(45deg);
    top: 0;
  }
  
  .menu-toggle[aria-expanded="true"] .hamburger::after {
    transform: rotate(-45deg);
    top: 0;
  }
}
</style>
