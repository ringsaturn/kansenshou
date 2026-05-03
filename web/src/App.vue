<template>
  <div id="app">
    <header class="app-header">
      <div class="container header-inner">
        <div class="header-title-row">
          <h1>感染症データ検索システム</h1>
          <a href="https://github.com/ringsaturn/kansenshou" target="_blank" rel="noopener noreferrer" class="github-link" aria-label="GitHub Repository">
            <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
          </a>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-link">ホーム</router-link>
          <router-link to="/ari" class="nav-link">急性呼吸器感染症</router-link>
          <router-link to="/teiten" class="nav-link">定点報告</router-link>
          <router-link to="/zensu" class="nav-link">全数報告</router-link>
          <router-link to="/trend" class="nav-link">過去10年トレンド</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <div class="container">
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
  background-color: #fbfbfd;
  color: #1d1d1f;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 22px;
}

.app-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.28, 0.11, 0.32, 1);
}

.app-header .container {
  padding: 16px 22px;
}

.header-inner {
  display: flex;
  flex-direction: column;
}

.header-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.header-title-row h1 {
  margin-bottom: 0;
}

.github-link {
  display: flex;
  align-items: center;
  color: #6e6e73;
  transition: color 0.2s;
  flex-shrink: 0;
}

.github-link:hover {
  color: #1d1d1f;
}

.app-header h1 {
  font-size: 21px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #1d1d1f;
}

.nav-menu {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.nav-link {
  color: #1d1d1f;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 980px;
  transition: all 0.3s cubic-bezier(0.28, 0.11, 0.32, 1);
  font-weight: 400;
  font-size: 14px;
  letter-spacing: -0.01em;
}

.nav-link:hover {
  background-color: rgba(0, 0, 0, 0.04);
  color: #000;
}

.nav-link.router-link-active {
  background-color: #000;
  color: #fff;
}

.app-main {
  padding: 60px 0 100px;
  min-height: calc(100vh - 160px);
}

.card {
  background: #fff;
  border-radius: 18px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  margin-bottom: 30px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.5s cubic-bezier(0.28, 0.11, 0.32, 1);
}

.card:hover {
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.card h2 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 32px;
  color: #1d1d1f;
  letter-spacing: -0.02em;
}

.filters {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 32px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  font-size: 12px;
  color: #6e6e73;
  letter-spacing: 0.01em;
  text-transform: uppercase;
}

.filter-group select,
.filter-group input {
  padding: 11px 16px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 12px;
  font-size: 15px;
  min-width: 160px;
  background: #fff;
  color: #1d1d1f;
  font-family: inherit;
  transition: all 0.2s cubic-bezier(0.28, 0.11, 0.32, 1);
}

.filter-group select:hover,
.filter-group input:hover {
  border-color: rgba(0, 0, 0, 0.24);
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #0071e3;
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
}

.data-table-wrapper {
  overflow-x: auto;
  margin-top: 28px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead {
  background-color: #f5f5f7;
  position: sticky;
  top: 0;
}

.data-table th {
  padding: 14px 12px;
  text-align: left;
  font-weight: 500;
  color: #6e6e73;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  white-space: nowrap;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.data-table td {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
}

.data-table tbody tr {
  transition: background-color 0.2s cubic-bezier(0.28, 0.11, 0.32, 1);
}

.data-table tbody tr:hover {
  background-color: #f5f5f7;
}

.loading {
  text-align: center;
  padding: 80px 20px;
  font-size: 17px;
  color: #6e6e73;
  font-weight: 400;
}

.error {
  background-color: #fff5f5;
  color: #c41e3a;
  padding: 16px 20px;
  border-radius: 12px;
  margin: 24px 0;
  border: 1px solid rgba(196, 30, 58, 0.2);
  font-size: 14px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: linear-gradient(135deg, #000 0%, #1d1d1f 100%);
  color: white;
  padding: 32px 28px;
  border-radius: 16px;
  text-align: left;
  transition: all 0.4s cubic-bezier(0.28, 0.11, 0.32, 1);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
}

.stat-card .stat-label {
  font-size: 13px;
  opacity: 0.7;
  margin-bottom: 12px;
  font-weight: 400;
  letter-spacing: 0.01em;
}

.stat-card .stat-value {
  font-size: 48px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

button {
  background: #0071e3;
  color: white;
  border: none;
  padding: 11px 22px;
  border-radius: 980px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 400;
  transition: all 0.3s cubic-bezier(0.28, 0.11, 0.32, 1);
  font-family: inherit;
  letter-spacing: -0.01em;
}

button:hover {
  background: #0077ed;
  transform: scale(1.02);
}

button:active {
  transform: scale(0.98);
}

button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  transform: none;
}

.data-source {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  text-align: center;
}

.data-source p {
  color: #6e6e73;
  font-size: 13px;
  line-height: 1.7;
  letter-spacing: -0.01em;
}

.data-source a {
  color: #0071e3;
  text-decoration: none;
  transition: color 0.2s;
  word-break: break-all;
}

.data-source a:hover {
  color: #0077ed;
  text-decoration: underline;
}
</style>
