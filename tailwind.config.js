/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: '#0A0B14',
        surface: '#13141F',
        elevated: '#1C1E2E',
        primary: '#5B6AF0',
        secondary: '#7B8FF7',
        success: '#3ECF8E',
        warning: '#F59E0B',
        destructive: '#EF4444',
        'text-primary': '#F0F1FA',
        'text-secondary': '#8A8FA8',
        'text-tertiary': '#52566E',
        border: '#232538',
      },
      fontFamily: {
        display: ['var(--font-display)', 'sans-serif'],
        body: ['var(--font-body)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      boxShadow: {
        'card': '0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04)',
      },
      transitionTimingFunction: {
        'bounce-custom': 'cubic-bezier(0.25,0.46,0.45,0.94)',
      }
    },
  },
  plugins: [],
}
