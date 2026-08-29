import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import { FrappeUI, setConfig, frappeRequest, call } from 'frappe-ui'

function mount() {
  let app = createApp(App)
  setConfig('resourceFetcher', frappeRequest)
  app.use(router)
  app.use(FrappeUI, { socketio: false })
  app.mount('#app')
}

if (import.meta.env.DEV) {
  // vite dev server doesn't render the {{ csrf_token }} jinja placeholder,
  // so fetch it separately before mounting.
  call('neer_jal.www.neer_jal.get_context_for_dev').then((values) => {
    window.csrf_token = values.csrf_token
    mount()
  })
} else {
  mount()
}
