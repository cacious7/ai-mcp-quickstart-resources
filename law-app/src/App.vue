<template>
  <div id="app">
    <OfflineNotification />
    <AppHeader />
    <main class="main-content">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import OfflineNotification from '@/components/notifications/OfflineNotification.vue'
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}

/* Remove default padding for full-width views */
.main-content :deep(.chat-view),
.main-content :deep(.home-view) {
  margin: 0;
  padding: 0;
  max-width: none;
}
</style>
