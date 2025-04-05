/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        singlife: {
          red: '#ea3326', // Primary red
          dark: '#1e1e1e', // Dark color
          white: '#ffffff', // White
          light: '#eeeeee', // Light gray
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}; 