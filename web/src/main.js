import { createApp } from "vue";
import { createRouter, createWebHashHistory } from "vue-router";
import App from "./App.vue";
import Home from "./views/Home.vue";
import ARIView from "./views/ARIView.vue";
import TeitenView from "./views/TeitenView.vue";
import ZensuView from "./views/ZensuView.vue";
import TrendView from "./views/TrendView.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/ari", component: ARIView },
  { path: "/teiten", component: TeitenView },
  { path: "/zensu", component: ZensuView },
  { path: "/trend", component: TrendView },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

const app = createApp(App);
app.use(router);
app.mount("#app");
