/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
  "./src/components/**/*.{ts,tsx}",
  "./src/app/**/*.{ts,tsx}",
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        indigo: {
          500: '#6366F1',
          600: '#4F46E5',
          700: '#4338CA'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    }
  },
  plugins: []
}
