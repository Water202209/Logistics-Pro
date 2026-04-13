<template>
  <div id="app">
    <div v-if="isLoginPage" class="login-page">
      <router-view />
    </div>
    <div v-else class="main-layout">
      <Sidebar />
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const isLoginPage = computed(() => route.path === '/')
</script>

<style>
/* 全局重置 */
* { margin: 0; padding: 0; box-sizing: border-box; }

html, body {
  width: 100%; height: 100%;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-attachment: fixed;
}

#app { width: 100%; min-height: 100vh; }

.login-page { min-height: 100vh; }

.main-layout {
  display: flex;
  width: 100%;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 32px;
  background: rgba(242, 242, 247, 0.5);
  min-height: 100vh;
  width: calc(100% - 260px);
  transition: all 0.3s ease;
}

/* 响应式断点 */
@media (max-width: 1200px) { .main-content { padding: 24px; } }
@media (max-width: 992px) {
  .main-content { margin-left: 220px; width: calc(100% - 220px); padding: 20px; }
}
@media (max-width: 768px) {
  .main-layout { flex-direction: column; }
  .main-content { margin-left: 0; width: 100%; padding: 16px; }
}
</style>