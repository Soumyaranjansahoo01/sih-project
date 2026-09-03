/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        railway: {
          dark: '#0f172a',
          navy: '#1e293b',
          blue: '#1d4ed8',
          accent: '#0284c7',
          gold: '#f59e0b',
          emerald: '#10b981',
          crimson: '#ef4444'
        }
      }
    },
  },
  plugins: [],
}
