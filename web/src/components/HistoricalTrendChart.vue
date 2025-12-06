<template>
  <div class="chart-container">
    <v-chart :key="chartKey" :option="chartOption" :style="{ height: height }" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  MarkLineComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  MarkLineComponent
])

export default {
  name: 'HistoricalTrendChart',
  components: {
    VChart
  },
  props: {
    title: {
      type: String,
      default: '過去10年間トレンド'
    },
    data: {
      type: Array,
      required: true
    },
    disease: {
      type: String,
      required: true
    },
    height: {
      type: String,
      default: '500px'
    }
  },
  data() {
    return {}
  },
  computed: {
    chartKey() {
      if (!this.data || this.data.length === 0) return this.disease

      const first = this.data[0]
      const last = this.data[this.data.length - 1]
      const fingerprint = [
        this.data.length,
        first?.年,
        first?.週,
        first?.定当,
        last?.年,
        last?.週,
        last?.定当
      ].join('-')

      return `${this.disease}-${fingerprint}`
    },
    chartOption() {
      // Group data by year
      const yearGroups = {}
      this.data.forEach(item => {
        if (!yearGroups[item.年]) {
          yearGroups[item.年] = []
        }
        yearGroups[item.年].push(item)
      })

      // Get all weeks for X axis
      const weeks = [...new Set(this.data.map(item => item.週))].sort((a, b) => a - b)
      const xData = weeks.map(w => `第${w}週`)

      // Get year list and sort
      const years = Object.keys(yearGroups).sort((a, b) => b - a)
      const latestYear = years[0]

      // Color configuration
      const latestYearColor = '#ff3b30'
      const historicalColors = [
        '#0071e3', '#34c759', '#ff9500', '#af52de',
        '#5ac8fa', '#ffcc00', '#ff2d55', '#30b0c7',
        '#32ade6', '#64d2ff'
      ]

      // Create series data
      const seriesData = years.map((year, index) => {
        const yearData = yearGroups[year]
        const yData = weeks.map(week => {
          const found = yearData.find(d => d.週 === week)
          return found ? found.定当 : null
        })

        const isLatest = year === latestYear
        const color = isLatest ? latestYearColor : historicalColors[index % historicalColors.length]

        return {
          name: `${year}年`,
          type: 'line',
          data: yData,
          smooth: true,
          symbol: isLatest ? 'circle' : 'none',
          symbolSize: isLatest ? 6 : 0,
          lineStyle: {
            width: isLatest ? 3 : 1.5,
            color: color,
            opacity: isLatest ? 1 : 0.6
          },
          itemStyle: {
            color: color
          },
          emphasis: {
            focus: 'series',
            lineStyle: {
              width: isLatest ? 4 : 2.5,
              opacity: 1
            }
          },
          z: isLatest ? 10 : 1
        }
      })

      // Calculate average values
      const avgData = weeks.map(week => {
        const values = years
          .filter(year => year !== latestYear)
          .map(year => {
            const found = yearGroups[year].find(d => d.週 === week)
            return found ? found.定当 : null
          })
          .filter(v => v !== null)

        if (values.length === 0) return null
        return values.reduce((a, b) => a + b, 0) / values.length
      })

      // Add average line series
      seriesData.push({
        name: '過去9年平均',
        type: 'line',
        data: avgData,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 2,
          color: '#86868b',
          type: 'dashed'
        },
        itemStyle: {
          color: '#86868b'
        },
        z: 5
      })

      const option = {
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
            color: '#1d1d1f',
            fontSize: 12
          },
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          formatter: (params) => {
            if (!params || params.length === 0) return ''

            let result = `<div style="font-weight: 600; margin-bottom: 8px;">${params[0].axisValue}</div>`

            // Sort by value
            const sorted = [...params].sort((a, b) => {
              const valA = a.value !== null ? a.value : -Infinity
              const valB = b.value !== null ? b.value : -Infinity
              return valB - valA
            })

            sorted.forEach(param => {
              if (param.value !== null && param.value !== undefined) {
                const isLatest = param.seriesName === `${latestYear}年`
                const style = isLatest ? 'font-weight: 600;' : ''
                const valueText = typeof param.value === 'number' ? param.value.toFixed(2) : param.value
                result += `${param.marker}<span style="${style}">${param.seriesName}: ${valueText}</span><br/>`
              }
            })

            return result
          }
        },
        legend: {
          data: seriesData.map(s => s.name),
          top: 45,
          textStyle: {
            fontSize: 11,
            color: '#6e6e73'
          },
          type: 'scroll',
          pageIconColor: '#0071e3',
          pageTextStyle: {
            color: '#6e6e73'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: 120,
          containLabel: true
        },
        toolbox: {
          feature: {
            dataZoom: {
              yAxisIndex: 'none',
              title: {
                zoom: 'ズーム',
                back: '戻る'
              }
            },
            restore: {
              title: 'リセット'
            },
            saveAsImage: {
              title: '画像として保存',
              name: this.title
            }
          },
          top: 45,
          right: 20
        },
        dataZoom: [
          {
            type: 'slider',
            start: 0,
            end: 100,
            height: 25,
            bottom: 35
          }
        ],
        xAxis: {
          type: 'category',
          data: xData,
          boundaryGap: false,
          axisLabel: {
            rotate: 45,
            fontSize: 11,
            color: '#6e6e73'
          },
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '定点当たり',
          nameTextStyle: {
            color: '#6e6e73',
            fontSize: 12
          },
          axisLabel: {
            fontSize: 11,
            color: '#6e6e73',
            formatter: (value) => {
              if (value >= 10000) return (value / 10000).toFixed(1) + '万'
              if (value >= 1000) return (value / 1000).toFixed(1) + 'k'
              return value.toFixed(1)
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
        series: seriesData
      }

      return option
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
