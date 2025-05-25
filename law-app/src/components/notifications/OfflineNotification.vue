<template>
  <Transition name="slide-down">
    <div v-if="isOffline" class="offline-notification">
      <WarningIcon class="offline-icon" />
      <span>You are currently offline. Some features may be limited.</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import WarningIcon from '@/components/icons/WarningIcon.vue'

const isOffline = ref(false)

// Check initial status
onMounted(() => {
  isOffline.value = !navigator.onLine
  
  // Listen for online/offline events
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
  
  // Listen for custom events (from service worker)
  document.addEventListener('app:online', handleOnline)
  document.addEventListener('app:offline', handleOffline)
})

// Clean up event listeners
onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
  document.removeEventListener('app:online', handleOnline)
  document.removeEventListener('app:offline', handleOffline)
})

// Event handlers
function handleOnline() {
  isOffline.value = false
}

function handleOffline() {
  isOffline.value = true
}
</script>

<style scoped>
.offline-notification {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: #f44336;
  color: white;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.offline-icon {
  margin-right: 8px;
  width: 20px;
  height: 20px;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
