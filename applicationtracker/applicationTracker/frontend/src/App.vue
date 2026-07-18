<template>
  <router-view></router-view>
</template>

<script setup>
</script>

<style>
/* Global Styles Moved From Dashboard */
:root {
  --primary-color: #CA6180;
  --primary-hover: #b35671;
  --bg-color: #9ED3DC;
  --card-bg: #FEFD99;
  --secondary-color: #FCB7C7;
  --text-main: #2c3e50;
  --text-muted: #575757;
  --border-color: #FCB7C7;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-main);
  margin: 0;
  padding: 0;
}

/* Base UI Definitions */
.card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-muted);
}

.form-group input, .form-group select {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  outline: none;
}

.form-group input:focus, .form-group select:focus {
  border-color: var(--primary-color);
}

button {
  cursor: pointer;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-danger {
  background-color: #ef4444;
  color: white;
  padding: 0.4rem 0.8rem;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn-danger.outline {
  background-color: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.btn-danger.outline:hover {
  background-color: #ef4444;
  color: white;
}
</style>