import path from 'path'
import fs from 'fs'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

// Everything (HTML shell, JS/CSS, manifest, service worker, icons) is served
// under the single /neer_jal/ prefix so the service worker's default scope
// covers the whole app - see hooks.py's website_route_rules for the other half.
const APP_BASE = '/neer_jal/'

export default defineConfig({
  base: APP_BASE,
  plugins: [
    vue(),
    VitePWA({
      base: APP_BASE,
      registerType: 'autoUpdate',
      injectRegister: 'auto',
      manifestFilename: 'manifest.json',
      includeAssets: ['favicon.svg'],
      manifest: {
        id: '/neer_jal',
        name: 'Neer Jal',
        short_name: 'Neer Jal',
        description: 'Record water can deliveries, returns and payments',
        start_url: '/neer_jal',
        scope: '/neer_jal/',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#1d4ed8',
        icons: [
          {
            src: 'manifest/manifest-icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: 'manifest/manifest-icon-192.maskable.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'maskable',
          },
          {
            src: 'manifest/manifest-icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: 'manifest/manifest-icon-512.maskable.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        navigateFallback: '/neer_jal',
        // don't intercept API/desk/file calls - only cache our own app shell + assets
        navigateFallbackDenylist: [/^\/api\//, /^\/app\//, /^\/assets\//, /^\/files\//],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 8080,
    proxy: getProxyOptions(),
  },
  build: {
    outDir: path.resolve(__dirname, '../neer_jal/www/neer_jal'),
    emptyOutDir: true,
    target: 'es2015',
  },
})

function getProxyOptions() {
  const config = getCommonSiteConfig()
  const webserver_port = config ? config.webserver_port : 8000
  return {
    '^/(app|api|assets|files|private)': {
      target: `http://127.0.0.1:${webserver_port}`,
      ws: true,
      router: function (req) {
        const site_name = req.headers.host.split(':')[0]
        return `http://${site_name}:${webserver_port}`
      },
    },
  }
}

function getCommonSiteConfig() {
  let currentDir = path.resolve('.')
  while (currentDir !== path.resolve('/')) {
    const configPath = path.join(currentDir, 'sites', 'common_site_config.json')
    if (fs.existsSync(configPath)) {
      return JSON.parse(fs.readFileSync(configPath))
    }
    currentDir = path.resolve(currentDir, '..')
  }
  return null
}
