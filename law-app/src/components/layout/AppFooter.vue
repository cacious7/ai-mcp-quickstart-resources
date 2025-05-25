<template>
  <footer class="app-footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-section">
          <h6>Legal AI Assistant</h6>
          <p class="footer-description">
            AI-powered legal information for Zambian laws. 
            This tool provides general information only and does not constitute legal advice.
          </p>
        </div>
        
        <div class="footer-section">
          <h6>Quick Links</h6>
          <ul class="footer-links">
            <li><RouterLink to="/about">About</RouterLink></li>
            <li><RouterLink to="/disclaimer">Disclaimer</RouterLink></li>
            <li><RouterLink to="/chat">Ask AI</RouterLink></li>
            <li><RouterLink to="/laws">Browse Laws</RouterLink></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h6>Important Notice</h6>
          <p class="disclaimer-text">
            This application provides general legal information only. 
            For specific legal advice, please consult a qualified legal professional.
          </p>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; {{ currentYear }} Zambian Legal AI Assistant. All rights reserved.</p>
        <p class="version-info">Version 1.0.0 MVP</p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-footer {
  background-color: var(--text-primary);
  color: white;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-xl);
  padding: var(--space-xxl) 0 var(--space-xl) 0;
}

.footer-section h6 {
  color: var(--primary-light);
  margin-bottom: var(--space-md);
  font-size: 1.1rem;
}

.footer-description,
.disclaimer-text {
  color: #bdbdbd;
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 0;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: var(--space-sm);
}

.footer-links a {
  color: #bdbdbd;
  text-decoration: none;
  transition: color var(--transition-fast);
  font-size: 0.9rem;
}

.footer-links a:hover {
  color: var(--primary-light);
  text-decoration: none;
}

.footer-bottom {
  border-top: 1px solid #424242;
  padding: var(--space-lg) 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-md);
}

.footer-bottom p {
  margin: 0;
  color: #bdbdbd;
  font-size: 0.875rem;
}

.version-info {
  font-size: 0.8rem;
  color: #757575;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: var(--space-lg);
    text-align: center;
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
    gap: var(--space-sm);
  }
}
</style>
