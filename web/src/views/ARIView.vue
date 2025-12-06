<template>
  <div class="ari-view">
    <div class="card">
      <h2>急性呼吸器感染症データ</h2>

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
            <div class="stat-value">{{ filteredData.length }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">都道府県数</div>
            <div class="stat-value">{{ uniquePrefectures.length }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">週の範囲</div>
            <div class="stat-value">{{ weekRange }}</div>
          </div>
        </div>

        <!-- View Toggle -->
        <div class="view-toggle">
          <button :class="{ active: viewMode === 'chart' }" @click="viewMode = 'chart'">
            📊 グラフ表示
          </button>
          <button :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">
            📋 テーブル表示
          </button>
        </div>

        <div class="filters">
          <div class="filter-group">
            <label>年</label>
            <select v-model="filters.year">
              <option value="">すべて</option>
              <option v-for="year in uniqueYears" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>週</label>
            <select v-model="filters.week">
              <option value="">すべて</option>
              <option v-for="week in uniqueWeeks" :key="week" :value="week">第{{ week }}週</option>
            </select>
          </div>

          <div class="filter-group">
            <label>都道府県</label>
            <select v-model="filters.prefecture">
              <option value="">すべて（全国）</option>
              <option v-for="pref in uniquePrefectures" :key="pref" :value="pref">{{ pref }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="resetFilters">フィルタをリセット</button>
          </div>
        </div>

        <!-- Chart View -->
        <div v-if="viewMode === 'chart'" class="chart-view">
          <div v-if="filters.prefecture === ''">
            <div class="chart-section">
              <h3>急性呼吸器感染症 - 全国報告数推移（総数）</h3>
              <TimeSeriesChart title="急性呼吸器感染症 全国報告数推移（総数）" :data="nationalChartData" xField="週ラベル" yField="急性呼吸器感染症_報告"
                seriesName="報告数" :showArea="true" height="450px" />
            </div>

            <div class="chart-section">
              <h3>急性呼吸器感染症 - 定点当たり報告数推移（総数）</h3>
              <TimeSeriesChart title="急性呼吸器感染症 定点当たり報告数推移（総数）" :data="nationalChartData" xField="週ラベル"
                yField="急性呼吸器感染症_定当" seriesName="定点当たり" height="400px" />
            </div>

            <div class="chart-section">
              <h3>急性呼吸器感染症 - 都道府県別比較 (Top 15)</h3>
              <PrefectureComparisonChart title="急性呼吸器感染症 都道府県別報告数" :data="prefectureComparisonData"
                valueField="急性呼吸器感染症_報告" :topN="15" height="600px" />
            </div>
          </div>
          <div v-else>
            <div class="chart-section">
              <h3>{{ filters.prefecture }} - 急性呼吸器感染症</h3>
              <MultiSeriesChart :title="`${filters.prefecture} - 急性呼吸器感染症`" :data="chartData" xField="週ラベル" :series="[
                { field: '急性呼吸器感染症_報告', name: '報告数', color: '#0071e3' },
                { field: '急性呼吸器感染症_定当', name: '定点当たり', color: '#34c759' }
              ]" height="450px" />
            </div>
          </div>
        </div>

        <!-- Table View -->
        <div v-else>
          <div class="data-table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>年</th>
                  <th>週</th>
                  <th>月</th>
                  <th>開始日</th>
                  <th>終了日</th>
                  <th>都道府県</th>
                  <th>報告数</th>
                  <th>定当</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in paginatedData" :key="index">
                  <td>{{ row.年 }}</td>
                  <td>{{ row.週 }}</td>
                  <td>{{ row.月 }}</td>
                  <td>{{ row.開始日 }}</td>
                  <td>{{ row.終了日 }}</td>
                  <td>{{ row.都道府県 }}</td>
                  <td>{{ formatNumber(row.急性呼吸器感染症_報告) }}</td>
                  <td>{{ formatNumber(row.急性呼吸器感染症_定当) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination" v-if="totalPages > 1">
            <button @click="prevPage" :disabled="currentPage === 1">前へ</button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }} ページ</span>
            <button @click="nextPage" :disabled="currentPage === totalPages">次へ</button>
          </div>
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
import MultiSeriesChart from '../components/MultiSeriesChart.vue'
import PrefectureComparisonChart from '../components/PrefectureComparisonChart.vue'
import HistoricalComparisonWidget from '../components/HistoricalComparisonWidget.vue'

export default {
  name: 'ARIView',
  components: {
    TimeSeriesChart,
    MultiSeriesChart,
    PrefectureComparisonChart,
    HistoricalComparisonWidget
  },
  data() {
    return {
      data: [],
      loading: true,
      error: null,
      filters: {
        year: '',
        week: '',
        prefecture: ''
      },
      currentPage: 1,
      itemsPerPage: 50,
      viewMode: 'chart' // 'chart' or 'table'
    }
  },
  computed: {
    uniqueYears() {
      return [...new Set(this.data.map(row => row.年))].sort((a, b) => b - a)
    },
    uniqueWeeks() {
      return [...new Set(this.data.map(row => row.週))].sort((a, b) => a - b)
    },
    uniquePrefectures() {
      const prefectureOrder = [
        '北海道',
        '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
        '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
        '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県',
        '三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
        '鳥取県', '島根県', '岡山県', '広島県', '山口県',
        '徳島県', '香川県', '愛媛県', '高知県',
        '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
      ]
            // Exclude total, as empty value represents nationwide (すべて)
      const prefs = [...new Set(this.data.map(row => row.都道府県))]
        .filter(pref => pref && pref !== '総数' && prefectureOrder.includes(pref))
      return prefs.sort((a, b) => {
        const indexA = prefectureOrder.indexOf(a)
        const indexB = prefectureOrder.indexOf(b)
        return indexA - indexB
      })
    },
    weekRange() {
      if (this.uniqueWeeks.length === 0) return '-'
      return `${Math.min(...this.uniqueWeeks)}-${Math.max(...this.uniqueWeeks)}`
    },
    filteredData() {
      const filtered = this.data.filter(row => {
        if (this.filters.year && row.年 !== this.filters.year) return false
        if (this.filters.week && row.週 !== this.filters.week) return false
        // Empty prefecture means nationwide (総数), otherwise match specific prefecture
        if (this.filters.prefecture) {
          if (row.都道府県 !== this.filters.prefecture) return false
        } else {
          // When no prefecture selected, only show total data
          if (row.都道府県 !== '総数') return false
        }
        return true
      })
      // Sort by year and week in descending order (newest first)
      return filtered.sort((a, b) => {
        if (a.年 !== b.年) return b.年 - a.年
        return b.週 - a.週
      })
    },
    totalPages() {
      return Math.ceil(this.filteredData.length / this.itemsPerPage)
    },
    paginatedData() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredData.slice(start, end)
    },
    chartData() {
      // Prepare data for chart, add week label field
      return this.filteredData.map(row => ({
        ...row,
        週ラベル: `${row.年}年第${row.週}週`
      }))
    },
    nationalChartData() {
      // National trend chart data: only use total
      return this.chartData.filter(row => row.都道府県 === '総数')
    },
    prefectureComparisonData() {
      // Prefecture comparison data: filter from raw data, apply year and week filters, but don't restrict prefecture
      const filtered = this.data.filter(row => {
        if (this.filters.year && row.年 !== this.filters.year) return false
        if (this.filters.week && row.週 !== this.filters.week) return false
        if (row.都道府県 === '総数') return false // Exclude total
        return true
      })
      return filtered.sort((a, b) => {
        if (a.年 !== b.年) return b.年 - a.年
        return b.週 - a.週
      })
    },
    latestDataPoint() {
      // Get latest data point for historical comparison
      if (this.chartData.length === 0) return null
      return this.chartData[0] // chartData is already sorted by time in descending order
    },
    latestNationalDataPoint() {
      // Get latest nationwide total data point for historical comparison (not affected by prefecture filter)
      const nationalData = this.data
        .filter(row => row.都道府県 === '総数')
        .sort((a, b) => {
          if (a.年 !== b.年) return b.年 - a.年
          return b.週 - a.週
        })
      if (nationalData.length === 0) return null
      return nationalData[0]
    }
  },
  watch: {
    filteredData() {
      this.currentPage = 1
    }
  },
  methods: {
    async loadData() {
      try {
        const response = await fetch('/data/ari/merged_ari.csv')
        const csvText = await response.text()
        this.data = parseCSV(csvText)
        this.loading = false
      } catch (err) {
        this.error = 'データの読み込みに失敗しました: ' + err.message
        this.loading = false
      }
    },
    formatNumber(value) {
      if (value === null || value === undefined || value === '') return '-'
      return parseFloat(value).toLocaleString()
    },
    resetFilters() {
      this.filters = {
        year: '',
        week: '',
        prefecture: ''
      }
    },
    prevPage() {
      if (this.currentPage > 1) this.currentPage--
    },
    nextPage() {
      if (this.currentPage < this.totalPages) this.currentPage++
    }
  },
  mounted() {
    this.loadData()
  }
}
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
  padding: 32px 0;
}

.page-info {
  font-weight: 400;
  color: #6e6e73;
  font-size: 14px;
  letter-spacing: -0.01em;
}

.view-toggle {
  display: flex;
  gap: 12px;
  margin: 24px 0;
  justify-content: center;
}

.view-toggle button {
  padding: 10px 24px;
  border: 1px solid #d2d2d7;
  background: #fff;
  border-radius: 980px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.28, 0.11, 0.32, 1);
  color: #1d1d1f;
}

.view-toggle button:hover {
  border-color: #0071e3;
  color: #0071e3;
}

.view-toggle button.active {
  background: #0071e3;
  color: #fff;
  border-color: #0071e3;
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
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}
</style>
