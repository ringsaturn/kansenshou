<template>
  <div class="home">
    <div class="card welcome-card">
      <h1>感染症データ検索システムへようこそ</h1>
      <p class="welcome-text">
        本システムは、日本の感染症関連データの検索および表示機能を提供します。急性呼吸器感染症、定点報告、全数報告のデータが含まれます。
      </p>

      <div class="data-sources">
        <div class="source-card">
          <h3>急性呼吸器感染症 (ARI)</h3>
          <p>急性呼吸器感染症の報告データ。地域と時間別に集計されています。</p>
          <router-link to="/ari">
            <button>データを見る</button>
          </router-link>
        </div>

        <div class="source-card">
          <h3>定点報告 (Teiten)</h3>
          <p>各種感染症の定点医療機関報告データ。インフルエンザ、咽頭炎など多数の疾患を含みます。</p>
          <router-link to="/teiten">
            <button>データを見る</button>
          </router-link>
        </div>

        <div class="source-card">
          <h3>全数報告 (Zensu)</h3>
          <p>法定感染症の全数報告データ。全面的な監視が必要な各種感染症を網羅しています。</p>
          <router-link to="/zensu">
            <button>データを見る</button>
          </router-link>
        </div>

        <div class="source-card">
          <h3>過去10年トレンド (Trend)</h3>
          <p>過去10年間の定点当たり報告数の推移データ。歴史的なトレンドと現在の状況を比較できます。</p>
          <router-link to="/trend">
            <button>データを見る</button>
          </router-link>
        </div>
      </div>

      <div class="data-notice">
        <div class="notice-section">
          <h3>データ出典</h3>
          <p>
            国立健康危機管理研究機構 感染症情報提供サイトのデータを加工して作成<br>
            <a href="https://id-info.jihs.go.jp/surveillance/idwr/" target="_blank" rel="noopener noreferrer">
              https://id-info.jihs.go.jp/surveillance/idwr/
            </a><br>
            利用規約:
            <a href="https://id-info.jihs.go.jp/usage-contract.html" target="_blank" rel="noopener noreferrer">
              https://id-info.jihs.go.jp/usage-contract.html
            </a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  text-align: center;
  padding: 60px 40px;
}

.welcome-card h1 {
  color: #1d1d1f;
  font-size: 56px;
  font-weight: 600;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.welcome-text {
  font-size: 21px;
  color: #6e6e73;
  margin-bottom: 64px;
  line-height: 1.5;
  letter-spacing: -0.01em;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}

.data-sources {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-top: 48px;
}

.source-card {
  background: #f5f5f7;
  padding: 36px 32px;
  border-radius: 18px;
  transition: all 0.4s cubic-bezier(0.28, 0.11, 0.32, 1);
  border: 1px solid rgba(0, 0, 0, 0.04);
  text-align: left;
}

.source-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
  background: #fff;
}

.source-card h3 {
  color: #1d1d1f;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}

.source-card p {
  color: #6e6e73;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 28px;
  min-height: 72px;
  letter-spacing: -0.01em;
}

.source-card button {
  width: 100%;
  padding: 13px 24px;
  font-size: 15px;
}

.data-notice {
  margin-top: 80px;
  padding-top: 64px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  text-align: left;
}

.notice-section {
  margin-bottom: 40px;
}

.notice-section h3 {
  color: #1d1d1f;
  font-size: 21px;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}

.notice-section p,
.notice-section ul {
  color: #6e6e73;
  font-size: 15px;
  line-height: 1.7;
  letter-spacing: -0.01em;
}

.notice-section a {
  color: #0071e3;
  text-decoration: none;
  transition: color 0.2s;
}

.notice-section a:hover {
  color: #0077ed;
  text-decoration: underline;
}

.notice-section ul {
  list-style: none;
  padding: 0;
}

.notice-section ul li {
  padding-left: 24px;
  position: relative;
  margin-bottom: 12px;
}

.notice-section ul li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #0071e3;
  font-weight: bold;
}
</style>
