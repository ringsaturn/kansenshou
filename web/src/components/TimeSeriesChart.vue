<template>
  <div class="chart-container">
    <v-chart :option="chartOption" :style="{ height: height }" autoresize />
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
  ToolboxComponent
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
  ToolboxComponent
])

export default {
  name: 'TimeSeriesChart',
  components: {
    VChart
  },
  props: {
    title: {
      type: String,
      default: '時系列チャート'
    },
    data: {
      type: Array,
      required: true
    },
    xField: {
      type: String,
      default: '開始日'
    },
    yField: {
      type: String,
      required: true
    },
    seriesName: {
      type: String,
      default: 'データ'
    },
    height: {
      type: String,
      default: '400px'
    },
    smooth: {
      type: Boolean,
      default: true
    },
    showArea: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    chartOption() {
      // Sort data by time (from old to new) - reverse array
      const sortedData = [...this.data].reverse()

      const xData = sortedData.map(item => item[this.xField])
      const yData = sortedData.map(item => {
        const val = item[this.yField]
        return val === null || val === undefined || val === '' || val === '-' ? null : parseFloat(val)
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
          formatter: (params) => {
            if (!params || params.length === 0) return ''
            const param = params[0]
            const value = param.value !== null ? param.value.toLocaleString() : '-'
            return `${param.axisValue}<br/>${param.marker}${param.seriesName}: <b>${value}</b>`
          }
        },
        legend: {
          data: [this.seriesName],
          top: 40,
          textStyle: {
            fontSize: 12,
            color: '#6e6e73'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: 80,
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
            bottom: 30,
            textStyle: {
              fontSize: 10
            }
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
        series: [
          {
            name: this.seriesName,
            type: 'line',
            data: yData,
            smooth: this.smooth,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              width: 2.5,
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
              }
            },
            itemStyle: {
              color: '#0071e3'
            },
            areaStyle: this.showArea ? {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(0, 113, 227, 0.3)' },
                  { offset: 1, color: 'rgba(0, 113, 227, 0.05)' }
                ]
              }
            } : undefined,
            emphasis: {
              focus: 'series',
              itemStyle: {
                borderColor: '#fff',
                borderWidth: 2
              }
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
