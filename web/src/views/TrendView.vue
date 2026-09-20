<template>
  <div class="trend-view">
    <div class="card">
      <h2>{{ $t('trend.title', { range: yearRangeText }) }}</h2>

      <div v-if="loading" class="loading">
        {{ $t('common.loading') }}
      </div>

      <div v-else-if="error" class="error">
        {{ error }}
      </div>

      <div v-else>
        <div class="stats">
          <div class="stat-card">
            <div class="stat-label">{{ $t('stats.totalRecords') }}</div>
            <div class="stat-value">{{ data.length }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">{{ $t('stats.diseaseCount') }}</div>
            <div class="stat-value">{{ uniqueDiseases.length }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">{{ $t('stats.reportWeekRange') }}</div>
            <div class="stat-value">{{ reportWeekRange }}</div>
          </div>
        </div>

        <div class="filters">
          <div class="filter-group">
            <label>{{ $t('common.reportYear') }}</label>
            <select v-model="filters.reportYear">
              <option value="">{{ $t('common.all') }}</option>
              <option v-for="year in uniqueReportYears" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>{{ $t('common.reportWeek') }}</label>
            <select v-model="filters.reportWeek">
              <option value="">{{ $t('common.all') }}</option>
              <option v-for="week in uniqueReportWeeks" :key="week" :value="week">{{ $t('common.weekOption', { week }) }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>{{ $t('common.disease') }}</label>
            <select v-model="filters.disease">
              <option value="">{{ $t('common.selectPlaceholder') }}</option>
              <option v-for="disease in uniqueDiseases" :key="disease" :value="disease">{{ $disease(disease) }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="resetFilters">{{ $t('common.resetFilters') }}</button>
          </div>
        </div>

        <!-- Chart View -->
        <div v-if="filters.disease" class="chart-view">
          <div class="chart-section">
            <h3>{{ $t('trend.comparison', { disease: diseaseName, range: yearRangeText }) }}</h3>
            <p class="chart-description">
              <template v-if="filters.reportYear && filters.reportWeek">{{ $t('trend.comparisonDesc', { year: filters.reportYear, week: filters.reportWeek, range: yearRangeText }) }}</template>
              <template v-else>{{ $t('trend.comparisonDescLatest', { range: yearRangeText }) }}</template>
            </p>
            <HistoricalTrendChart :title="$t('trend.comparisonChart', { disease: diseaseName, range: yearRangeText })" :data="chartData"
              :disease="filters.disease" height="500px" />
          </div>

          <div class="chart-section" v-if="latestYearData.length > 0">
            <h3>{{ $t('trend.latestYearDetail', { disease: diseaseName }) }}</h3>
            <TimeSeriesChart :title="$t('trend.latestYearChart', { disease: diseaseName, year: latestYear })" :data="latestYearData" xField="週"
              :yField="String(latestYear)" :seriesName="$t('common.yearLabel', { year: latestYear })" :showArea="true" height="400px" />
          </div>

          <div class="chart-section">
            <h3>{{ $t('trend.heatmap', { disease: diseaseName }) }}</h3>
            <p class="chart-description">
              {{ $t('trend.heatmapDesc', { range: yearRangeText }) }}
            </p>
            <HeatmapCalendarChart :title="$t('trend.heatmapChart', { disease: diseaseName })" :data="chartData" :disease="filters.disease"
              height="650px" />
          </div>
        </div>

        <div v-else class="chart-notice">
          {{ $t('common.selectDiseaseToChart') }}
        </div>

        <div class="data-source">
          <p>
            {{ $t('common.dataSource') }}<br>
            <a href="https://id-info.jihs.go.jp/surveillance/idwr/" target="_blank" rel="noopener noreferrer">
              https://id-info.jihs.go.jp/surveillance/idwr/
            </a><br>
            <a href="https://id-info.jihs.go.jp/usage-contract.html" target="_blank" rel="noopener noreferrer">
              {{ $t('common.terms') }}
            </a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { parseCSV } from '../utils/csvParser.js'
import { loadCSVFromZip } from '../utils/zipLoader.js'
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
    diseaseName() {
      return this.$disease(this.filters.disease)
    },
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
        // Use reduce instead of Math.max(...spread): the dataset has >100k rows and spreading overflows the call stack
        const latestYear = this.data.reduce((m, row) => (row.報告年 > m ? row.報告年 : m), -Infinity)
        const latestWeekData = this.data.filter(row => row.報告年 === latestYear)
        const latestWeek = latestWeekData.reduce((m, row) => (row.週 > m ? row.週 : m), -Infinity)
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
          const weekNumInt = parseInt(weekNum)
          const value = row[weekCol]

          // Skip if weekNum is not a valid number or value is empty
          if (isNaN(weekNumInt) || value === null || value === undefined || value === '') {
            return
          }

          result.push({
            報告年: row.報告年,
            報告週: row.報告週,
            疾病: row.疾病,
            年: row.年,
            週: weekNumInt,
            週ラベル: this.$t('common.weekOption', { week: weekNum }),
            定当: parseFloat(value)
          })
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
      
      // Get data for the latest year (historical data year, not report year)
      // chartData structure: {報告年, 報告週, 疾病, 年, 週, 週ラベル, 定当}
      // We want to show all available weeks for the latest historical year
      const latestYearChartData = this.chartData.filter(d => d.年 == this.latestYear)
      
      // Group by week number (週) to get unique weeks
      // Since the same week might appear in multiple report dates, we take the latest report
      const dataMap = new Map()
      latestYearChartData.forEach(d => {
        const weekKey = d.週
        const existing = dataMap.get(weekKey)
        // Keep the data from the latest report year/week
        if (!existing || d.報告年 > existing.報告年 || 
            (d.報告年 === existing.報告年 && d.報告週 > existing.報告週)) {
          dataMap.set(weekKey, {
            週: d.週,  // Already a number from chartData
            週ラベル: d.週ラベル,
            定当: d.定当
          })
        }
      })
      
      // Sort by week number in descending order (latest first)
      // TimeSeriesChart reverses the data, so descending input becomes ascending display
      const sortedData = Array.from(dataMap.values())
        .sort((a, b) => b.週 - a.週)
        .map(d => ({
          週: d.週ラベル,
          週番号: d.週,
          [String(this.latestYear)]: d.定当
        }))
      
      return sortedData
    },
    yearRangeText() {
      if (this.chartData.length === 0) return this.$t('trend.pastTenYears')
      const years = [...new Set(this.chartData.map(d => d.年))].sort((a, b) => a - b)
      if (years.length === 0) return this.$t('trend.pastTenYears')

      const yearCount = years.length
      const minYear = years[0]
      const maxYear = years[years.length - 1]

      // If only one year of data
      if (yearCount === 1) {
        return this.$t('common.yearLabel', { year: minYear })
      }

      // If years are consecutive, show the count
      const isConsecutive = years.every((year, i) => i === 0 || year === years[i - 1] + 1)
      if (isConsecutive) {
        return this.$t('trend.pastYears', { n: yearCount })
      }

      // Otherwise show year range
      return this.$t('common.yearLabel', { year: `${minYear}-${maxYear}` })
    }
  },
  watch: {
    'filters.disease'(val) {
      this.$router.replace({ query: { ...this.$route.query, disease: val || undefined } })
    },
  },
  methods: {
    async loadData() {
      try {
        const csvText = await loadCSVFromZip('/data/trend/merged_trend.zip')
        this.data = parseCSV(csvText)
        this.loading = false
        const q = this.$route.query.disease
        if (q && this.uniqueDiseases.includes(q)) this.filters.disease = q
      } catch (err) {
        this.error = this.$t('common.loadError', { msg: err.message })
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
