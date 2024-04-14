// router/index.js or a similar file where you define your Vue Router routes

import Vue from 'vue';
import VueRouter from 'vue-router';
import InteraktivnyTest from '../views/interaktivny_test.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/interactive-test',
    name: 'InteractiveTest',
    component: InteraktivnyTest,
    props: true // This allows the component to receive props via route parameters
  },
  // other routes...
];

const router = new VueRouter({
  // mode, base, and other router options...
  routes,
});

export default router;
