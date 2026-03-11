<template>
  <section class="panel">
    <h2 class="panel-title">404 - Lost in the Network</h2>
    <p class="muted">This page does not exist on either the forum or netdisk operator route.</p>
    <RouterLink to="/forum">Go to Forum</RouterLink>
    <span class="muted"> | </span>
    <RouterLink to="/netdisk">Go to Netdisk</RouterLink>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
