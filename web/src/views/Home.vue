<template>
  <div class="home">
    <div class="card welcome-card">
      <h1>{{ $t('home.title') }}</h1>
      <p class="welcome-text">
        {{ $t('home.intro') }}
      </p>

      <div v-if="activeAlerts.length > 0" class="alerts-section">
        <h2 class="alerts-title">{{ $t('home.alertsTitle') }}</h2>
        <div class="alerts-grid">
          <div v-for="alert in activeAlerts" :key="alert.issue_title" class="alert-card">
            <div class="alert-card-header">
              <span class="alert-disease">{{ $disease(alert.disease) }}</span>
              <span class="alert-dataset-tag">{{ alert.dataset === 'teiten' ? $t('nav.teiten') : $t('nav.zensu') }}</span>
            </div>
            <p class="alert-start">
              {{ $t('home.alertStart', { year: alert.alert_start_year, month: String(alert.alert_start_month).padStart(2, '0'), week: String(alert.alert_start_week).padStart(2, '0') }) }}
            </p>
            <div class="alert-stats">
              <div class="alert-stat">
                <span class="stat-num">{{ alert.weeks_active }}</span>
                <span class="stat-label">{{ $t('home.weeksActive') }}</span>
              </div>
              <div class="alert-stat">
                <span class="stat-num">{{ alert.ratio }}x</span>
                <span class="stat-label">{{ $t('home.ratio') }}</span>
              </div>
              <div class="alert-stat">
                <span class="stat-num">{{ alert.current_value?.toLocaleString() }}</span>
                <span class="stat-label">{{ $t('home.currentWeekCount') }}</span>
              </div>
            </div>
            <router-link :to="{ path: alert.dataset === 'teiten' ? '/teiten' : '/zensu', query: { disease: alert.disease } }">
              <button class="alert-btn">{{ $t('home.viewData') }}</button>
            </router-link>
          </div>
        </div>
      </div>

      <div class="data-sources">
        <div class="source-card">
          <h3>{{ $t('home.ariTitle') }}</h3>
          <p>{{ $t('home.ariDesc') }}</p>
          <router-link to="/ari">
            <button>{{ $t('home.viewData') }}</button>
          </router-link>
        </div>

        <div class="source-card">
          <h3>{{ $t('home.teitenTitle') }}</h3>
          <p>{{ $t('home.teitenDesc') }}</p>
          <router-link to="/teiten">
            <button>{{ $t('home.viewData') }}</button>
          </router-link>
        </div>

        <div class="source-card">
          <h3>{{ $t('home.zensuTitle') }}</h3>
          <p>{{ $t('home.zensuDesc') }}</p>
          <router-link to="/zensu">
            <button>{{ $t('home.viewData') }}</button>
          </router-link>
        </div>

        <div class="source-card">
          <h3>{{ $t('home.trendTitle') }}</h3>
          <p>{{ $t('home.trendDesc') }}</p>
          <router-link to="/trend">
            <button>{{ $t('home.viewData') }}</button>
          </router-link>
        </div>
      </div>

      <div class="data-notice">
        <div class="notice-section">
          <h3>{{ $t('home.dataSourceTitle') }}</h3>
          <p>
            {{ $t('home.dataSourceBody') }}<br>
            <a href="https://id-info.jihs.go.jp/surveillance/idwr/" target="_blank" rel="noopener noreferrer">
              https://id-info.jihs.go.jp/surveillance/idwr/
            </a><br>
            {{ $t('home.termsLabel') }}
            <a href="https://id-info.jihs.go.jp/usage-contract.html" target="_blank" rel="noopener noreferrer">
              https://id-info.jihs.go.jp/usage-contract.html
            </a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      activeAlerts: [],
    }
  },
  async mounted() {
    try {
      const resp = await fetch('/data/trend_alerts.json')
      if (resp.ok) {
        const data = await resp.json()
        this.activeAlerts = data.active_alerts || []
      }
    } catch {
      // alerts unavailable — silently skip
    }
  },
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  text-align: center;
  padding: 60px 40px;
}

.welcome-card h1 {
  color: #1d1d1f;
  font-size: 56px;
  font-weight: 600;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.welcome-text {
  font-size: 21px;
  color: #6e6e73;
  margin-bottom: 64px;
  line-height: 1.5;
  letter-spacing: -0.01em;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}

.data-sources {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-top: 48px;
}

.source-card {
  background: #f5f5f7;
  padding: 36px 32px;
  border-radius: 18px;
  transition: all 0.4s cubic-bezier(0.28, 0.11, 0.32, 1);
  border: 1px solid rgba(0, 0, 0, 0.04);
  text-align: left;
}

.source-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
  background: #fff;
}

.source-card h3 {
  color: #1d1d1f;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}

.source-card p {
  color: #6e6e73;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 28px;
  min-height: 72px;
  letter-spacing: -0.01em;
}

.source-card button {
  width: 100%;
  padding: 13px 24px;
  font-size: 15px;
}

.data-notice {
  margin-top: 80px;
  padding-top: 64px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  text-align: left;
}

.notice-section {
  margin-bottom: 40px;
}

.notice-section h3 {
  color: #1d1d1f;
  font-size: 21px;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}

.notice-section p,
.notice-section ul {
  color: #6e6e73;
  font-size: 15px;
  line-height: 1.7;
  letter-spacing: -0.01em;
}

.notice-section a {
  color: #0071e3;
  text-decoration: none;
  transition: color 0.2s;
}

.notice-section a:hover {
  color: #0077ed;
  text-decoration: underline;
}

.notice-section ul {
  list-style: none;
  padding: 0;
}

.notice-section ul li {
  padding-left: 24px;
  position: relative;
  margin-bottom: 12px;
}

.notice-section ul li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #0071e3;
  font-weight: bold;
}

/* --- Alert section --- */
.alerts-section {
  margin-top: 56px;
  text-align: left;
}

.alerts-title {
  font-size: 21px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.01em;
  margin-bottom: 20px;
}

.alerts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.alert-card {
  background: #fff8f0;
  border: 1px solid rgba(255, 149, 0, 0.25);
  border-left: 4px solid #ff9500;
  border-radius: 14px;
  padding: 24px 20px;
  text-align: left;
  transition: box-shadow 0.2s;
}

.alert-card:hover {
  box-shadow: 0 4px 20px rgba(255, 149, 0, 0.15);
}

.alert-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}

.alert-disease {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.01em;
}

.alert-dataset-tag {
  font-size: 11px;
  font-weight: 500;
  color: #ff9500;
  background: rgba(255, 149, 0, 0.12);
  padding: 2px 8px;
  border-radius: 20px;
  white-space: nowrap;
}

.alert-start {
  font-size: 12px;
  color: #6e6e73;
  margin-bottom: 16px;
}

.alert-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.alert-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-num {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 11px;
  color: #6e6e73;
}

.alert-btn {
  width: 100%;
  padding: 10px 16px;
  font-size: 14px;
  background: #ff9500;
  color: #fff;
  border: none;
}

.alert-btn:hover {
  background: #e68600;
}
</style>
