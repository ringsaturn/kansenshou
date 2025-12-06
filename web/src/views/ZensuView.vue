<template>
  <div class="zensu-view">
    <div class="card">
      <h2>全数報告データ</h2>

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
              <option value="">すべて</option>
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
                <th v-for="col in displayColumns" :key="col">{{ shortenColumnName(col) }}</th>
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

export default {
  name: 'ZensuView',
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
      itemsPerPage: 30
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
      const prefs = [...new Set(this.data.map(row => row.都道府県))]
        .filter(pref => pref && (pref === '総数' || prefectureOrder.includes(pref)))
      return prefs.sort((a, b) => {
        if (a === '総数') return -1
        if (b === '総数') return 1
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
        const disease = col.replace(/_報告|_累積/g, '')
        diseases.add(disease)
      })
      return [...diseases].sort()
    },
    displayColumns() {
      if (!this.selectedDisease) {
        return this.diseaseColumns.slice(0, 8) // Default display first 8 columns
      }
      return this.diseaseColumns.filter(col => col.includes(this.selectedDisease))
    },
    filteredData() {
      const filtered = this.data.filter(row => {
        if (this.filters.year && row.年 !== this.filters.year) return false
        if (this.filters.week && row.週 !== this.filters.week) return false
        if (this.filters.prefecture && row.都道府県 !== this.filters.prefecture) return false
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
        const response = await fetch('/data/zensu/merged_zensu.csv')
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
      if (value === '-') return '-'
      const num = parseFloat(value)
      if (isNaN(num)) return value
      return num.toLocaleString()
    },
    shortenColumnName(col) {
      return col.length > 15 ? col.substring(0, 13) + '...' : col
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
</style>
