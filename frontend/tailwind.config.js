/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          900: '#070a12',
          800: '#0b1120',
          700: '#151f38',
          600: '#1e294b',
          500: '#334155',
          accent: '#06b6d4',
          accentGlow: '#0891b2',
          danger: '#f43f5e',
          warning: '#f59e0b',
          success: '#10b981'
        }
      }
    },
  },
  plugins: [],
}

