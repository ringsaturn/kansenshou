import { createI18n } from 'vue-i18n'
import ja from './locales/ja.js'
import zh from './locales/zh.js'
import { translateDisease } from './diseases.js'
import { translatePrefecture } from './prefectures.js'

export const SUPPORTED_LOCALES = ['ja', 'zh']
const STORAGE_KEY = 'kansenshou-locale'

function detectLocale() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (SUPPORTED_LOCALES.includes(saved)) return saved
  } catch {
    // localStorage unavailable (private mode etc.) — fall through
  }
  const nav = (navigator.language || '').toLowerCase()
  return nav.startsWith('zh') ? 'zh' : 'ja'
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: detectLocale(),
  fallbackLocale: 'ja',
  messages: { ja, zh },
})

export function setLocale(locale) {
  if (!SUPPORTED_LOCALES.includes(locale)) return
  i18n.global.locale.value = locale
  document.documentElement.lang = locale === 'zh' ? 'zh-CN' : 'ja'
  document.title = i18n.global.t('app.docTitle')
  try {
    localStorage.setItem(STORAGE_KEY, locale)
  } catch {
    // ignore
  }
}

// Vue plugin: installs vue-i18n and adds display-name helpers for data values.
// Data keys (column names, prefecture names, disease names) stay in Japanese;
// these helpers translate only at render time.
export default {
  install(app) {
    app.use(i18n)
    const locale = () => i18n.global.locale.value
    app.config.globalProperties.$disease = (name) => translateDisease(name, locale())
    app.config.globalProperties.$pref = (name) => translatePrefecture(name, locale())
    // Translate a data column like "インフルエンザ_定当" → "流感_每定点"
    app.config.globalProperties.$column = (col) => {
      const m = /^(.*)_(報告|定当|累積)$/.exec(col)
      if (!m) return translateDisease(col, locale())
      const suffixKey = { 報告: 'common.reportCount', 定当: 'common.perSentinel', 累積: 'common.cumulative' }[m[2]]
      return `${translateDisease(m[1], locale())}_${i18n.global.t(suffixKey)}`
    }
    setLocale(locale())
  },
}
