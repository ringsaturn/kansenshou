<template>
  <div class="chart-container">
    <v-chart :option="chartOption" :style="{ height: height }" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  ToolboxComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  ToolboxComponent
])

export default {
  name: 'PrefectureComparisonChart',
  components: {
    VChart
  },
  props: {
    title: {
      type: String,
      default: '都道府県別比較'
    },
    data: {
      type: Array,
      required: true
    },
    valueField: {
      type: String,
      required: true
    },
    topN: {
      type: Number,
      default: 10
    },
    height: {
      type: String,
      default: '500px'
    }
  },
  computed: {
    chartOption() {
      // Aggregate data for each prefecture
      const prefectureData = {}
      this.data.forEach(item => {
        const pref = item.都道府県
        if (pref === '総数') return // Skip total

        const value = item[this.valueField]
        const numValue = value === null || value === undefined || value === '' || value === '-' ? 0 : parseFloat(value)

        if (!prefectureData[pref]) {
          prefectureData[pref] = 0
        }
        prefectureData[pref] += numValue
      })

      // Sort and take Top N
      const sortedData = Object.entries(prefectureData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, this.topN)

      const prefectures = sortedData.map(item => item[0])
      const values = sortedData.map(item => item[1])

      return {
        title: {
          text: this.title,
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 600,
            color: '#1d1d1f'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e0e0e0',
          borderWidth: 1,
          textStyle: {
            color: '#1d1d1f'
          },
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params) => {
            if (!params || params.length === 0) return ''
            const param = params[0]
            return `${param.name}<br/>${param.marker}合計: <b>${param.value.toLocaleString()}</b>`
          }
        },
        grid: {
          left: '5%',
          right: '4%',
          bottom: '3%',
          top: 80,
          containLabel: true
        },
        toolbox: {
          feature: {
            saveAsImage: {
              title: '画像として保存',
              name: this.title
            }
          },
          top: 40,
          right: 20
        },
        xAxis: {
          type: 'value',
          axisLabel: {
            fontSize: 11,
            color: '#6e6e73',
            formatter: (value) => {
              if (value >= 10000) return (value / 10000).toFixed(1) + '万'
              if (value >= 1000) return (value / 1000).toFixed(1) + 'k'
              return value.toLocaleString()
            }
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          splitLine: {
            lineStyle: {
              color: '#f0f0f0',
              type: 'dashed'
            }
          }
        },
        yAxis: {
          type: 'category',
          data: prefectures,
          axisLabel: {
            fontSize: 12,
            color: '#1d1d1f'
          },
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          },
          axisTick: {
            show: false
          }
        },
        series: [
          {
            type: 'bar',
            data: values,
            itemStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 1,
                y2: 0,
                colorStops: [
                  { offset: 0, color: '#0071e3' },
                  { offset: 1, color: '#06c' }
                ]
              },
              borderRadius: [0, 4, 4, 0]
            },
            emphasis: {
              itemStyle: {
                color: {
                  type: 'linear',
                  x: 0,
                  y: 0,
                  x2: 1,
                  y2: 0,
                  colorStops: [
                    { offset: 0, color: '#005bb5' },
                    { offset: 1, color: '#0051a3' }
                  ]
                }
              }
            },
            label: {
              show: true,
              position: 'right',
              fontSize: 11,
              color: '#6e6e73',
              formatter: (params) => params.value.toLocaleString()
            }
          }
        ]
      }
    }
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  margin: 20px 0;
}
</style>
