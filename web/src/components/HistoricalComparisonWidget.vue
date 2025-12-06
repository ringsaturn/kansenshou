<template>
  <div class="historical-comparison">
    <div class="comparison-header">
      <h3>📊 {{ comparisonTitle }}</h3>
    </div>

    <div class="comparison-content">
      <div v-if="loading" class="loading-text">
        過去データを読み込み中...
      </div>

      <div v-else-if="error" class="error-text">
        {{ error }}
      </div>

      <div v-else-if="hasHistoricalData">
        <div class="comparison-stats">
          <div class="stat-item">
            <div class="stat-label">現在の値</div>
            <div class="stat-value" :class="comparisonClass">{{ currentValue }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">過去平均 ({{ historicalYearsCount }}年間)</div>
            <div class="stat-value">{{ historicalAverage }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">過去最高</div>
            <div class="stat-value">{{ historicalMax }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">比較</div>
            <div class="stat-value" :class="comparisonClass">
              {{ comparisonText }}
            </div>
          </div>
        </div>

        <HistoricalTrendChart :title="`${disease} - ${comparisonTitle}`" :data="chartData" :disease="disease" height="450px" />
      </div>

      <div v-else class="no-data-text">
        この週のデータは過去のトレンドデータに含まれていません
      </div>
    </div>
  </div>
</template>

<script>
import { parseCSV } from '../utils/csvParser.js'
import HistoricalTrendChart from './HistoricalTrendChart.vue'

export default {
  name: 'HistoricalComparisonWidget',
  components: {
    HistoricalTrendChart
  },
  props: {
    disease: {
      type: String,
      required: true
    },
    currentYear: {
      type: [String, Number],
      required: true
    },
    currentWeek: {
      type: [String, Number],
      required: true
    },
    currentValue: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      trendData: [],
      loading: false,
      error: null
    }
  },
  computed: {
    hasHistoricalData() {
      return this.currentWeekData.length > 0
    },
    chartData() {
      if (!this.trendData || this.trendData.length === 0) return []

            // Use cache key to avoid redundant calculations
      const cacheKey = `${this.disease}-${this.currentYear}-${this.currentWeek}`
      if (this._cachedChartData && this._lastCacheKey === cacheKey) {
        return this._cachedChartData
      }

            // Filter data for relevant disease, and only use latest report week data
      let diseaseData = this.trendData.filter(row => row.疾病 === this.disease)

      if (diseaseData.length === 0) return []

      // Find latest report year and week
      const latestReportYear = Math.max(...diseaseData.map(row => row.報告年))
      const latestWeekData = diseaseData.filter(row => row.報告年 === latestReportYear)
      const latestReportWeek = Math.max(...latestWeekData.map(row => row.週))

            // Only use latest report week data
      diseaseData = diseaseData.filter(row =>
        row.報告年 === latestReportYear && row.週 === latestReportWeek
      )

      // Convert data format - return all week data for chart display
      const result = []
      const weekColumns = Object.keys(diseaseData[0] || {}).filter(key => key.endsWith('週'))

      diseaseData.forEach(row => {
        weekColumns.forEach(weekCol => {
          const weekNum = weekCol.replace('週', '')
          const value = row[weekCol]

          if (value !== null && value !== undefined && value !== '') {
            result.push({
              報告年: row.報告年,
              報告週: row.週,
              疾病: row.疾病,
              年: row.年,
              週: parseInt(weekNum),
              週ラベル: `第${weekNum}週`,
              定当: parseFloat(value)
            })
          }
        })
      })

      const sortedResult = result.sort((a, b) => {
        if (a.年 !== b.年) return a.年 - b.年
        return a.週 - b.週
      })

            // Cache result
      this._cachedChartData = sortedResult
      this._lastCacheKey = cacheKey

      return sortedResult
    },
    currentWeekData() {
      // Only get current week data for statistical calculation
      return this.chartData.filter(d => d.週 == this.currentWeek).sort((a, b) => a.年 - b.年)
    },
    historicalValues() {
      return this.currentWeekData
        .filter(d => d.年 != this.currentYear)
        .map(d => d.定当)
    },
    historicalYearsCount() {
      // Count actual number of historical years
      const years = new Set(this.currentWeekData
        .filter(d => d.年 != this.currentYear)
        .map(d => d.年))
      return years.size
    },
    comparisonTitle() {
      if (this.historicalYearsCount === 0) return '過去データとの比較'
      if (this.historicalYearsCount >= 10) return '過去10年間との比較'
      return `過去${this.historicalYearsCount}年間との比較`
    },
    historicalAverage() {
      if (this.historicalValues.length === 0) return '-'
      const sum = this.historicalValues.reduce((a, b) => a + b, 0)
      return (sum / this.historicalValues.length).toFixed(2)
    },
    historicalMax() {
      if (this.historicalValues.length === 0) return '-'
      return Math.max(...this.historicalValues).toFixed(2)
    },
    comparisonText() {
      if (this.historicalValues.length === 0) return '-'
      const avg = parseFloat(this.historicalAverage)
      const current = parseFloat(this.currentValue)
      const diff = ((current - avg) / avg * 100).toFixed(1)

      if (diff > 0) {
        return `+${diff}%`
      } else if (diff < 0) {
        return `${diff}%`
      } else {
        return '平均並み'
      }
    },
    comparisonClass() {
      if (this.historicalValues.length === 0) return ''
      const avg = parseFloat(this.historicalAverage)
      const current = parseFloat(this.currentValue)

      if (current > avg * 1.5) return 'high'
      if (current < avg * 0.5) return 'low'
      return 'normal'
    }
  },
  mounted() {
    // 组件挂载时自动加载数据
    this.loadTrendData()
  },
  methods: {
    async loadTrendData() {
      this.loading = true
      this.error = null

      try {
        // Check if there is global cache
        if (window.__trendDataCache) {
          this.trendData = window.__trendDataCache
          this.loading = false
          return
        }

        const response = await fetch('/data/trend/merged_trend.csv')
        const csvText = await response.text()
        const parsedData = parseCSV(csvText)

                // Cache to global to avoid redundant loading
        window.__trendDataCache = parsedData
        this.trendData = parsedData
      } catch (err) {
        this.error = '過去データの読み込みに失敗しました'
        console.error(err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.historical-comparison {
  margin-top: 32px;
  padding: 24px;
  background: #f5f5f7;
  border-radius: 12px;
  border: 1px solid #d2d2d7;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.comparison-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
}

.toggle-btn {
  padding: 8px 20px;
  background: #0071e3;
  color: #fff;
  border: none;
  border-radius: 980px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.28, 0.11, 0.32, 1);
}

.toggle-btn:hover {
  background: #0077ed;
  transform: scale(1.02);
}

.toggle-btn:active {
  transform: scale(0.98);
}

.comparison-content {
  margin-top: 20px;
}

.comparison-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #6e6e73;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
}

.stat-value.high {
  color: #ff3b30;
}

.stat-value.low {
  color: #34c759;
}

.stat-value.normal {
  color: #0071e3;
}

.loading-text,
.error-text,
.no-data-text {
  padding: 20px;
  text-align: center;
  color: #6e6e73;
  font-size: 14px;
}

.error-text {
  color: #ff3b30;
}
</style>
