import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// shared stylesheet (same file the HDA app uses) so both look alike
import '../../../shared/styles.css'

// DEMO (issue 3): uncomment to activate the "compromised" dependency. Once
// bundled it steals the token from localStorage and beacons it to the attacker
// listener (:5999). See DEMOS.md.
// import { track } from 'analytics-lite'

createApp(App).use(createPinia()).use(router).mount('#app')
