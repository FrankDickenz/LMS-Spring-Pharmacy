import typography from '@tailwindcss/typography'

export default {
  darkMode: 'class', // 👈 TARUH DI SINI
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    typography,
  ],
}
