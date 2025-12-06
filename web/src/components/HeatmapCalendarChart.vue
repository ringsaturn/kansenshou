<template>
  <div class="chart-container">
    <v-chart :option="chartOption" :style="{ height: height }" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { HeatmapChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  VisualMapComponent,
  ToolboxComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  VisualMapComponent,
  ToolboxComponent
])

export default {
  name: 'HeatmapCalendarChart',
  components: {
    VChart
  },
  props: {
    title: {
      type: String,
      default: '熱力カレンダー'
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
      default: '600px'
    }
  },
  computed: {
    chartOption() {
      // Group data by year
      const yearGroups = {}
      this.data.forEach(item => {
        if (!yearGroups[item.年]) {
          yearGroups[item.年] = []
        }
        yearGroups[item.年].push(item)
      })

      // Get year list and sort (display from old to new)
      const years = Object.keys(yearGroups).sort((a, b) => a - b)

      // Get all weeks
      const weeks = [...new Set(this.data.map(item => item.週))].sort((a, b) => a - b)

      // Prepare heatmap data [year index, week index, value]
      const heatmapData = []
      let maxValue = 0
      let minValue = Infinity

      years.forEach((year, yearIdx) => {
        const yearData = yearGroups[year]
        weeks.forEach((week, weekIdx) => {
          const found = yearData.find(d => d.週 === week)
          if (found && found.定当 !== null) {
            const value = found.定当
            heatmapData.push([weekIdx, yearIdx, value])
            maxValue = Math.max(maxValue, value)
            minValue = Math.min(minValue, value)
          }
        })
      })

      // Calculate appropriate color range
      const colorStops = [
        { value: 0, color: '#f0f9ff' },
        { value: minValue, color: '#bae6fd' },
        { value: (minValue + maxValue) / 4, color: '#7dd3fc' },
        { value: (minValue + maxValue) / 2, color: '#38bdf8' },
        { value: (minValue + maxValue) * 3 / 4, color: '#0ea5e9' },
        { value: maxValue * 0.9, color: '#0284c7' },
        { value: maxValue, color: '#ff3b30' }
      ]

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
          position: 'top',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e0e0e0',
          borderWidth: 1,
          textStyle: {
            color: '#1d1d1f'
          },
          formatter: (params) => {
            const year = years[params.value[1]]
            const week = weeks[params.value[0]]
            const value = params.value[2]
            return `<div style="font-weight: 600; margin-bottom: 4px;">${year}年 第${week}週</div>
                    定点当たり: <span style="font-weight: 600; color: #0071e3;">${value.toFixed(2)}</span>`
          }
        },
        grid: {
          left: '80',
          right: '50',
          top: '100',
          bottom: '80',
          containLabel: false
        },
        toolbox: {
          feature: {
            saveAsImage: {
              title: '画像として保存',
              name: this.title
            }
          },
          top: 45,
          right: 20
        },
        xAxis: {
          type: 'category',
          data: weeks.map(w => `${w}週`),
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(250,250,250,0.1)', 'rgba(250,250,250,0.3)']
            }
          },
          axisLabel: {
            fontSize: 10,
            color: '#6e6e73',
            interval: weeks.length > 40 ? 3 : (weeks.length > 20 ? 1 : 0),
            rotate: weeks.length > 30 ? 45 : 0
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
        yAxis: {
          type: 'category',
          data: years.map(y => `${y}年`),
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(250,250,250,0.1)', 'rgba(250,250,250,0.3)']
            }
          },
          axisLabel: {
            fontSize: 11,
            color: '#1d1d1f',
            fontWeight: (value) => {
              // Make latest year bold
              return value === `${years[years.length - 1]}年` ? 600 : 400
            }
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
        visualMap: {
          min: 0,
          max: maxValue,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '20',
          inRange: {
            color: colorStops.map(s => s.color)
          },
          text: ['高', '低'],
          textStyle: {
            color: '#6e6e73',
            fontSize: 11
          },
          formatter: (value) => {
            return value.toFixed(1)
          }
        },
        series: [
          {
            name: this.disease,
            type: 'heatmap',
            data: heatmapData,
            label: {
              show: false
            },
            emphasis: {
              itemStyle: {
                borderColor: '#333',
                borderWidth: 1
              }
            },
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 1
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
