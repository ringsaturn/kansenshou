import { markRaw } from "vue";
import { loadCSVFromZip } from "./zipLoader.js";
import { parseCSVAsync } from "./csvParser.js";

const DATASET_PATHS = {
  ari: "/data/ari/merged_ari.zip",
  teiten: "/data/teiten/merged_teiten.zip",
  zensu: "/data/zensu/merged_zensu.zip",
  trend: "/data/trend/merged_trend.zip",
};

// One in-flight/finished promise per dataset so it is downloaded and parsed
// at most once per session (TrendView and HistoricalComparisonWidget both need trend).
const cache = new Map();

/**
 * Load a merged dataset as an array of row objects.
 *
 * The returned array is wrapped in markRaw(): datasets have millions of cells
 * and never mutate, and Vue's deep reactive proxies make every computed that
 * iterates them 10-30x slower. Store it in component state as-is.
 *
 * @param {"ari"|"teiten"|"zensu"|"trend"} type
 * @returns {Promise<Array<Object>>}
 */
export function loadDataset(type) {
  const path = DATASET_PATHS[type];
  if (!path) return Promise.reject(new Error(`Unknown dataset: ${type}`));
  if (!cache.has(type)) {
    const promise = loadCSVFromZip(path)
      .then((csv) => parseCSVAsync(csv))
      .then((rows) => markRaw(rows))
      .catch((err) => {
        cache.delete(type); // allow retry after a failed load
        throw err;
      });
    cache.set(type, promise);
  }
  return cache.get(type);
}

// rows array -> { key -> Map<value, rows[]> }, built once per (rows, key)
const indexCache = new WeakMap();

/**
 * Group rows by the value of `key`, memoized per dataset. Scanning the trend
 * dataset (>150k rows) on every filter change costs ~100ms+ in the browser;
 * the grouped Map makes per-disease lookups O(1).
 * @param {Array<Object>} rows - a dataset returned by loadDataset()
 * @param {string} key - column name
 * @returns {Map<any, Array<Object>>}
 */
export function indexBy(rows, key) {
  let byKey = indexCache.get(rows);
  if (!byKey) {
    byKey = {};
    indexCache.set(rows, byKey);
  }
  if (!byKey[key]) {
    const map = new Map();
    for (const row of rows) {
      const v = row[key];
      const bucket = map.get(v);
      if (bucket) bucket.push(row);
      else map.set(v, [row]);
    }
    byKey[key] = markRaw(map);
  }
  return byKey[key];
}
