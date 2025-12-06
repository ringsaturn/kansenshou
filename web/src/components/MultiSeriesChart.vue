<template>
  <div class="chart-container">
    <v-chart :option="chartOption" :style="{ height: height }" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent
])

export default {
  name: 'MultiSeriesChart',
  components: {
    VChart
  },
  props: {
    title: {
      type: String,
      default: '比較チャート'
    },
    data: {
      type: Array,
      required: true
    },
    xField: {
      type: String,
      default: '開始日'
    },
    series: {
      type: Array,
      required: true,
      // Format: [{ field: 'インフルエンザ_報告', name: 'インフルエンザ', color: '#ff0000' }]
    },
    height: {
      type: String,
      default: '450px'
    },
    chartType: {
      type: String,
      default: 'line', // 'line' or 'bar'
      validator: (value) => ['line', 'bar'].includes(value)
    }
  },
  computed: {
    chartOption() {
      // Sort data by time (from old to new) - reverse array
      const sortedData = [...this.data].reverse()

      const xData = sortedData.map(item => item[this.xField])
      const colors = ['#0071e3', '#34c759', '#ff9500', '#ff3b30', '#af52de', '#5ac8fa', '#ffcc00', '#ff2d55']

      const seriesData = this.series.map((s, index) => {
        const yData = sortedData.map(item => {
          const val = item[s.field]
          return val === null || val === undefined || val === '' || val === '-' ? null : parseFloat(val)
        })

        const color = s.color || colors[index % colors.length]

        return {
          name: s.name,
          type: this.chartType,
          data: yData,
          smooth: true,
          symbol: 'circle',
          symbolSize: 4,
          lineStyle: this.chartType === 'line' ? {
            width: 2,
            color: color
          } : undefined,
          itemStyle: {
            color: color
          },
          emphasis: {
            focus: 'series'
          }
        }
      })

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
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        legend: {
          data: this.series.map(s => s.name),
          top: 40,
          textStyle: {
            fontSize: 12,
            color: '#6e6e73'
          },
          type: 'scroll'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: 100,
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
          top: 40,
          right: 20
        },
        dataZoom: [
          {
            type: 'slider',
            start: 0,
            end: 100,
            height: 20,
            bottom: 30
          }
        ],
        xAxis: {
          type: 'category',
          data: xData,
          boundaryGap: this.chartType === 'bar',
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
        series: seriesData
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
