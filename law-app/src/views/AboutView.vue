<template>
  <div class="about-page">
    <!-- Hero Section -->
    <section class="hero-section bg-primary text-white">
      <div class="container">
        <div class="hero-content text-center">
          <h1 class="hero-title">About Zambian Legal AI</h1>
          <p class="hero-subtitle">
            Democratizing access to Zambian legal information through artificial intelligence
          </p>
        </div>
      </div>
    </section>

    <!-- Mission Section -->
    <section class="section">
      <div class="container">
        <div class="grid-2">
          <div class="content-block">
            <h2>Our Mission</h2>
            <p class="text-large">
              To make Zambian law accessible to every citizen through the power of artificial intelligence,
              bridging the gap between complex legal language and everyday understanding.
            </p>
            <p>
              We believe that legal knowledge should not be confined to law libraries and legal professionals.
              Our platform uses advanced AI technology to simplify legal concepts, making them understandable
              for everyone while maintaining accuracy and relevance to Zambian law.
            </p>
          </div>
          <div class="image-placeholder">
            <div class="placeholder-content">
              <MissionIcon class="icon-large" />
              <p>Justice & Accessibility</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="section bg-gray-50">
      <div class="container">
        <div class="text-center mb-4">
          <h2>How It Works</h2>
          <p class="text-large">
            Our AI-powered platform combines advanced technology with legal expertise
          </p>
        </div>

        <div class="grid-3">
          <div class="feature-card">
            <div class="feature-icon">
              <AiIcon />
            </div>
            <h3>AI-Powered Analysis</h3>
            <p>
              Our local AI models process your legal questions using Retrieval-Augmented Generation (RAG)
              to provide accurate, contextual responses based on Zambian law.
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <DatabaseIcon />
            </div>
            <h3>Comprehensive Legal Database</h3>
            <p>
              Access to a curated database of Zambian laws, regulations, case law, and legal precedents,
              continuously updated and verified by legal experts.
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <ValidateIcon />
            </div>
            <h3>Human Validation</h3>
            <p>
              All AI responses are designed with human-in-the-loop validation to ensure accuracy
              and relevance to current Zambian legal standards.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Technology Section -->
    <section class="section">
      <div class="container">
        <div class="grid-2 reverse">
          <div class="image-placeholder">
            <div class="placeholder-content">
              <TechIcon class="icon-large" />
              <p>Advanced Technology</p>
            </div>
          </div>
          <div class="content-block">
            <h2>Technology Stack</h2>
            <p class="text-large">
              Built with modern, secure, and privacy-focused technologies
            </p>
            <ul class="feature-list">
              <li>
                <CheckIcon class="check-icon" />
                <strong>Local AI Models:</strong> Using Phi3 and other small language models for privacy and speed
              </li>
              <li>
                <CheckIcon class="check-icon" />
                <strong>RAG Architecture:</strong> Retrieval-Augmented Generation for accurate legal information
              </li>
              <li>
                <CheckIcon class="check-icon" />
                <strong>Vue 3 + TypeScript:</strong> Modern, type-safe frontend development
              </li>
              <li>
                <CheckIcon class="check-icon" />
                <strong>Privacy-First:</strong> Your data stays on your device with local processing
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Team Section -->
    <section class="section bg-gray-50">
      <div class="container">
        <div class="text-center mb-4">
          <h2>Our Commitment</h2>
          <p class="text-large">
            Dedicated to accuracy, accessibility, and ethical AI development
          </p>
        </div>

        <div class="grid-2">
          <div class="commitment-card">
            <div class="commitment-icon">
              <AccuracyIcon />
            </div>
            <h3>Accuracy & Reliability</h3>
            <p>
              We work with legal experts to ensure our AI provides accurate interpretations
              of Zambian law while clearly distinguishing between informational content and legal advice.
            </p>
          </div>

          <div class="commitment-card">
            <div class="commitment-icon">
              <PrivacyIcon />
            </div>
            <h3>Privacy & Security</h3>
            <p>
              Your legal queries are processed locally on your device. We don't store or transmit
              your personal legal questions, ensuring complete privacy and confidentiality.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact Section -->
    <section class="section">
      <div class="container">
        <div class="contact-section text-center">
          <h2>Get In Touch</h2>
          <p class="text-large mb-3">
            Have questions, suggestions, or feedback? We'd love to hear from you.
          </p>
          <div class="contact-info">
            <div class="contact-item">
              <EmailIcon />
              <span>info@zambianlegalai.com</span>
            </div>
            <div class="contact-item">
              <GithubIcon />
              <span>Open Source on GitHub</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Disclaimer Banner -->
    <section class="disclaimer-banner bg-warning-light">
      <div class="container">
        <div class="disclaimer-content">
          <WarningIcon class="warning-icon" />
          <div>
            <h4>Important Legal Disclaimer</h4>
            <p>
              This platform provides general legal information about Zambian law and should not be
              considered as legal advice. For specific legal matters, please consult with a qualified
              legal professional.
              <router-link to="/disclaimer" class="link-primary">Read full disclaimer</router-link>
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
// Import icon components (to be created)
import MissionIcon from '@/components/icons/MissionIcon.vue'
import AiIcon from '@/components/icons/AiIcon.vue'
import DatabaseIcon from '@/components/icons/DatabaseIcon.vue'
import ValidateIcon from '@/components/icons/ValidateIcon.vue'
import TechIcon from '@/components/icons/TechIcon.vue'
import CheckIcon from '@/components/icons/CheckIcon.vue'
import AccuracyIcon from '@/components/icons/AccuracyIcon.vue'
import PrivacyIcon from '@/components/icons/PrivacyIcon.vue'
import EmailIcon from '@/components/icons/EmailIcon.vue'
import GithubIcon from '@/components/icons/GithubIcon.vue'
import WarningIcon from '@/components/icons/WarningIcon.vue'

// Page metadata
import { useHead } from '@vueuse/head'

useHead({
  title: 'About - Zambian Legal AI',
  meta: [
    {
      name: 'description',
      content: 'Learn about Zambian Legal AI platform - our mission to democratize access to Zambian legal information through artificial intelligence and modern technology.'
    },
    {
      property: 'og:title',
      content: 'About Zambian Legal AI'
    },
    {
      property: 'og:description',
      content: 'Democratizing access to Zambian legal information through artificial intelligence'
    }
  ]
})
</script>

<style scoped>
.about-page {
  min-height: 100vh;
}

.hero-section {
  padding: 4rem 0;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
}

.content-block h2 {
  color: var(--color-primary);
  margin-bottom: 1.5rem;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gray-100);
  border-radius: var(--border-radius-lg);
  min-height: 300px;
}

.placeholder-content {
  text-align: center;
  color: var(--color-gray-600);
}

.icon-large {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.feature-icon {
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

.feature-list {
  list-style: none;
  padding: 0;
}

.feature-list li {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 0.75rem;
}

.check-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-success);
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.commitment-card {
  background: white;
  padding: 2rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.commitment-icon {
  width: 3rem;
  height: 3rem;
  background: var(--color-success-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: var(--color-success);
}

.contact-section {
  padding: 3rem 0;
}

.contact-info {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.disclaimer-banner {
  padding: 2rem 0;
  border-top: 1px solid var(--color-warning);
}

.disclaimer-content {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.warning-icon {
  width: 2rem;
  height: 2rem;
  color: var(--color-warning-dark);
  flex-shrink: 0;
}

.disclaimer-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--color-warning-dark);
}

.disclaimer-content p {
  margin: 0;
  color: var(--color-warning-dark);
}

.reverse {
  flex-direction: row-reverse;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .grid-2,
  .grid-3 {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .reverse {
    flex-direction: column;
  }

  .contact-info {
    flex-direction: column;
    gap: 1rem;
  }

  .disclaimer-content {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
