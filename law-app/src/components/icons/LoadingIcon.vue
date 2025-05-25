<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="loading-icon"
  >
    <path d="M21 12a9 9 0 11-6.219-8.56" />
    <animateTransform
      attributeName="transform"
      attributeType="XML"
      type="rotate"
      from="0 12 12"
      to="360 12 12"
      dur="1s"
      repeatCount="indefinite"
    />
  </svg>
</template>

<script setup lang="ts">
// Loading Icon - Represents loading state with animation
</script>

<style scoped>
.loading-icon {
  width: 1em;
  height: 1em;
  display: inline-block;
}
</style>
