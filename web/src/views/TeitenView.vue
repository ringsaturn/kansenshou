<template>
  <div class="teiten-view">
    <div class="card">
      <h2>定点報告データ</h2>

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
            <div class="stat-label">疾患種類</div>
            <div class="stat-value">{{ diseaseColumns.length }}</div>
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
            <label>表示する疾患</label>
            <select v-model="selectedDisease">
              <option value="">すべて</option>
              <option v-for="disease in diseaseList" :key="disease" :value="disease">{{ disease }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="resetFilters">フィルタをリセット</button>
          </div>
        </div>

        <!-- Chart View -->
        <div v-if="viewMode === 'chart'" class="chart-view">
          <div v-if="!selectedDisease" class="chart-notice">
            疾患を選択してグラフを表示してください
          </div>
          <div v-else-if="filters.prefecture === ''">
            <HistoricalComparisonWidget v-if="selectedDisease && latestNationalDataPoint"
              :disease="selectedDisease" :currentYear="latestNationalDataPoint.年" :currentWeek="latestNationalDataPoint.週"
              :currentValue="latestNationalDataPoint[`${selectedDisease}_定当`]" />

            <div class="chart-section">
              <h3>{{ selectedDisease }} - 全国推移（総数）</h3>
              <TimeSeriesChart :title="`${selectedDisease} 報告数推移（全国総数）`" :data="nationalChartData" xField="週ラベル"
                :yField="`${selectedDisease}_報告`" :seriesName="`${selectedDisease} 報告数`" :showArea="true"
                height="450px" />
            </div>

            <div class="chart-section">
              <h3>{{ selectedDisease }} - 定点当たり報告数推移（総数）</h3>
              <TimeSeriesChart :title="`${selectedDisease} 定点当たり報告数推移（全国総数）`" :data="nationalChartData" xField="週ラベル"
                :yField="`${selectedDisease}_定当`" :seriesName="`${selectedDisease} 定当`" height="400px" />
            </div>

            <div class="chart-section">
              <h3>{{ selectedDisease }} - 都道府県別比較 (Top 15)</h3>
              <PrefectureComparisonChart :title="`${selectedDisease} 都道府県別報告数`" :data="prefectureComparisonData"
                :valueField="`${selectedDisease}_報告`" :topN="15" height="600px" />
            </div>
          </div>
          <div v-else>
            <div class="chart-section">
              <h3>{{ filters.prefecture }} - {{ selectedDisease }}</h3>
              <MultiSeriesChart :title="`${filters.prefecture} - ${selectedDisease}`" :data="chartData" xField="週ラベル"
                :series="[
                  { field: `${selectedDisease}_報告`, name: '報告数', color: '#0071e3' },
                  { field: `${selectedDisease}_定当`, name: '定点当たり', color: '#34c759' }
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
                  <th v-for="col in displayColumns" :key="col">{{ col }}</th>
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
                  <td v-for="col in displayColumns" :key="col">{{ formatNumber(row[col]) }}</td>
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
import { loadCSVFromZip } from '../utils/zipLoader.js'
import TimeSeriesChart from '../components/TimeSeriesChart.vue'
import MultiSeriesChart from '../components/MultiSeriesChart.vue'
import PrefectureComparisonChart from '../components/PrefectureComparisonChart.vue'
import HistoricalComparisonWidget from '../components/HistoricalComparisonWidget.vue'

export default {
  name: 'TeitenView',
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
      selectedDisease: '',
      currentPage: 1,
      itemsPerPage: 30,
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
    diseaseColumns() {
      if (this.data.length === 0) return []
      const baseColumns = ['年', '週', '月', '開始日', '終了日', '都道府県']
      return Object.keys(this.data[0]).filter(key => !baseColumns.includes(key))
    },
    diseaseList() {
      const diseases = new Set()
      this.diseaseColumns.forEach(col => {
        const disease = col.replace(/_報告|_定当/g, '')
        diseases.add(disease)
      })
      return [...diseases].sort()
    },
    displayColumns() {
      if (!this.selectedDisease) {
        return this.diseaseColumns.slice(0, 6) // Default display first 6 columns
      }
      return this.diseaseColumns.filter(col => col.includes(this.selectedDisease))
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
      // 获取最新的数据点用于历史对比
      if (this.chartData.length === 0) return null
      return this.chartData[0] // chartData 已经按时间倒序排列
    },
    latestNationalDataPoint() {
      // 获取全国総数的最新数据点，用于历史对比（不受都道府県筛选影响）
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
    },
    selectedDisease(val) {
      this.$router.replace({ query: { ...this.$route.query, disease: val || undefined } })
    },
  },
  methods: {
    async loadData() {
      try {
        const csvText = await loadCSVFromZip('/data/teiten/merged_teiten.zip')
        this.data = parseCSV(csvText)
        this.loading = false
        const q = this.$route.query.disease
        if (q && this.diseaseList.includes(q)) this.selectedDisease = q
      } catch (err) {
        this.error = 'データの読み込みに失敗しました: ' + err.message
        this.loading = false
      }
    },
    formatNumber(value) {
      if (value === null || value === undefined || value === '') return '-'
      if (value === '-') return '-'
      const num = parseFloat(value)
      if (isNaN(num)) return value
      return num.toLocaleString()
    },
    resetFilters() {
      this.filters = {
        year: '',
        week: '',
        prefecture: ''
      }
      this.selectedDisease = ''
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
