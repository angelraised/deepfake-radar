/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui'] },
      colors: {
        ink: '#151515',
        panel: '#0d0d0d',
        electric: '#e9e9e9',
        violet: '#454545',
        destructive: '#ff6268',
        border: '#292929',
        muted: '#252525',
        secondary: '#262626',
        subtitle: '#bdb8b1',
        slate: {
          50: '#fafafa', 100: '#f4f4f4', 200: '#e9e9e9', 300: '#d2d2d2',
          400: '#a8a8a8', 500: '#7a7a7a', 600: '#5c5c5c', 700: '#454545',
          800: '#292929', 900: '#191919', 950: '#0d0d0d',
        },
      },
    },
  },
  plugins: [],
}

