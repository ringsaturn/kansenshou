<template>
  <div class="trend-view">
    <div class="card">
      <h2>{{ yearRangeText }}トレンドデータ</h2>

      <div v-if="loading" class="loading">
        データを読み込み中...
      </div>

      <div v-else-if="error" class="error">
        {{ error }}
      </div>

      <div v-else>
        <div class="stats">
          <div class="stat-card">
            <div class="stat-label">総データ件数</div>
            <div class="stat-value">{{ data.length }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">疾患種類</div>
            <div class="stat-value">{{ uniqueDiseases.length }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">報告週範囲</div>
            <div class="stat-value">{{ reportWeekRange }}</div>
          </div>
        </div>

        <div class="filters">
          <div class="filter-group">
            <label>報告年</label>
            <select v-model="filters.reportYear">
              <option value="">すべて</option>
              <option v-for="year in uniqueReportYears" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>報告週</label>
            <select v-model="filters.reportWeek">
              <option value="">すべて</option>
              <option v-for="week in uniqueReportWeeks" :key="week" :value="week">第{{ week }}週</option>
            </select>
          </div>

          <div class="filter-group">
            <label>疾患</label>
            <select v-model="filters.disease">
              <option value="">選択してください</option>
              <option v-for="disease in uniqueDiseases" :key="disease" :value="disease">{{ disease }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="resetFilters">フィルタをリセット</button>
          </div>
        </div>

        <!-- Chart View -->
        <div v-if="filters.disease" class="chart-view">
          <div class="chart-section">
            <h3>{{ filters.disease }} - {{ yearRangeText }}の推移比較</h3>
            <p class="chart-description">
              {{ filters.reportYear || '最新' }}年第{{ filters.reportWeek || '最新' }}週時点でのデータ。
              各線は{{ yearRangeText }}の同週における定点当たり報告数を示しています。
            </p>
            <HistoricalTrendChart :title="`${filters.disease} - ${yearRangeText}トレンド`" :data="chartData"
              :disease="filters.disease" height="500px" />
          </div>

          <div class="chart-section" v-if="latestYearData.length > 0">
            <h3>{{ filters.disease }} - 最新年度詳細</h3>
            <TimeSeriesChart :title="`${filters.disease} - ${latestYear}年 週別推移`" :data="latestYearData" xField="週"
              :yField="latestYear" :seriesName="`${latestYear}年`" :showArea="true" height="400px" />
          </div>

          <div class="chart-section">
            <h3>{{ filters.disease }} - 熱力カレンダー</h3>
            <p class="chart-description">
              {{ yearRangeText }}の週別データを色の濃淡で表示。濃い色は報告数が多く、薄い色は少ないことを示します。
              季節性パターンや年ごとの違いを視覚的に把握できます。
            </p>
            <HeatmapCalendarChart :title="`${filters.disease} - 週別熱力マップ`" :data="chartData" :disease="filters.disease"
              height="650px" />
          </div>
        </div>

        <div v-else class="chart-notice">
          疾患を選択してグラフを表示してください
        </div>

        <div class="data-source">
          <p>
            データ出典：国立健康危機管理研究機構 感染症情報提供サイトのデータを加工して作成<br>
            <a href="https://id-info.jihs.go.jp/surveillance/idwr/" target="_blank" rel="noopener noreferrer">
              https://id-info.jihs.go.jp/surveillance/idwr/
            </a><br>
            <a href="https://id-info.jihs.go.jp/usage-contract.html" target="_blank" rel="noopener noreferrer">
              利用規約
            </a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { parseCSV } from '../utils/csvParser.js'
import TimeSeriesChart from '../components/TimeSeriesChart.vue'
import HistoricalTrendChart from '../components/HistoricalTrendChart.vue'
import HeatmapCalendarChart from '../components/HeatmapCalendarChart.vue'

export default {
  name: 'TrendView',
  components: {
    TimeSeriesChart,
    HistoricalTrendChart,
    HeatmapCalendarChart
  },
  data() {
    return {
      data: [],
      loading: true,
      error: null,
      filters: {
        reportYear: '',
        reportWeek: '',
        disease: ''
      }
    }
  },
  computed: {
    uniqueReportYears() {
      return [...new Set(this.data.map(row => row.報告年))].sort((a, b) => b - a)
    },
    uniqueReportWeeks() {
      return [...new Set(this.data.map(row => row.週))].sort((a, b) => a - b)
    },
    uniqueDiseases() {
      return [...new Set(this.data.map(row => row.疾病))].filter(d => d).sort()
    },
    reportWeekRange() {
      if (this.uniqueReportWeeks.length === 0) return '-'
      return `${Math.min(...this.uniqueReportWeeks)}-${Math.max(...this.uniqueReportWeeks)}`
    },
    filteredData() {
      let filtered = this.data

      // If no report year/week selected, use latest report data by default
      if (!this.filters.reportYear && !this.filters.reportWeek) {
        // Find latest report year and week
        const latestYear = Math.max(...this.data.map(row => row.報告年))
        const latestWeekData = this.data.filter(row => row.報告年 === latestYear)
        const latestWeek = Math.max(...latestWeekData.map(row => row.週))
        filtered = this.data.filter(row => row.報告年 === latestYear && row.週 === latestWeek)
      } else {
        if (this.filters.reportYear) {
          filtered = filtered.filter(row => row.報告年 == this.filters.reportYear)
        }

        if (this.filters.reportWeek) {
          filtered = filtered.filter(row => row.週 == this.filters.reportWeek)
        }
      }

      if (this.filters.disease) {
        filtered = filtered.filter(row => row.疾病 === this.filters.disease)
      }

      return filtered
    },
    chartData() {
      // Prepare data for historical trend chart
      // Convert wide format data to chart-friendly format
      const result = []
      const weekColumns = Object.keys(this.data[0] || {}).filter(key => key.endsWith('週'))

      this.filteredData.forEach(row => {
        weekColumns.forEach(weekCol => {
          const weekNum = weekCol.replace('週', '')
          const value = row[weekCol]

          if (value !== null && value !== undefined && value !== '') {
            result.push({
              報告年: row.報告年,
              報告週: row.報告週,
              疾病: row.疾病,
              年: row.年,
              週: parseInt(weekNum),
              週ラベル: `第${weekNum}週`,
              定当: parseFloat(value)
            })
          }
        })
      })

      return result.sort((a, b) => a.週 - b.週)
    },
    latestYear() {
      if (this.chartData.length === 0) return null
      const years = [...new Set(this.chartData.map(d => d.年))].sort((a, b) => b - a)
      return years[0]
    },
    latestYearData() {
      if (!this.latestYear) return []
      return this.chartData
        .filter(d => d.年 == this.latestYear)
        .map(d => ({
          週: d.週ラベル,
          [this.latestYear]: d.定当
        }))
    },
    yearRangeText() {
      if (this.chartData.length === 0) return '過去10年間'
      const years = [...new Set(this.chartData.map(d => d.年))].sort((a, b) => a - b)
      if (years.length === 0) return '過去10年間'

      const yearCount = years.length
      const minYear = years[0]
      const maxYear = years[years.length - 1]

      // If only one year of data
      if (yearCount === 1) {
        return `${minYear}年`
      }

      // If years are consecutive, show the count
      const isConsecutive = years.every((year, i) => i === 0 || year === years[i - 1] + 1)
      if (isConsecutive) {
        return `過去${yearCount}年間`
      }

      // Otherwise show year range
      return `${minYear}-${maxYear}年`
    }
  },
  methods: {
    async loadData() {
      try {
        const response = await fetch('/data/trend/merged_trend.csv')
        const csvText = await response.text()
        this.data = parseCSV(csvText)
        this.loading = false
      } catch (err) {
        this.error = 'データの読み込みに失敗しました: ' + err.message
        this.loading = false
      }
    },
    resetFilters() {
      this.filters = {
        reportYear: '',
        reportWeek: '',
        disease: ''
      }
    }
  },
  mounted() {
    this.loadData()
  }
}
</script>

<style scoped>
.trend-view {
  max-width: 1400px;
  margin: 0 auto;
}

.chart-view {
  margin-top: 32px;
}

.chart-section {
  margin-bottom: 48px;
  padding: 24px;
  background: #fafafa;
  border-radius: 12px;
}

.chart-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 8px;
  letter-spacing: -0.01em;
}

.chart-description {
  font-size: 14px;
  color: #6e6e73;
  margin-bottom: 20px;
  line-height: 1.5;
}

.chart-notice {
  padding: 40px;
  text-align: center;
  color: #6e6e73;
  font-size: 16px;
  background: #fafafa;
  border-radius: 12px;
  margin: 24px 0;
}
</style>
