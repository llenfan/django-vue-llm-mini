<script setup>
import ArticleList from './components/ArticleList.vue'
</script>

<template>
  <div id="app">
    <main>
      <ArticleList />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: #2c3e50;
  background-color: #f8f9fa;
}

#app {
  min-height: 100vh;
}

main {
  padding: 20px 0;
}
</style>
