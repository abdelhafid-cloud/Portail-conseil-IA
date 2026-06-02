/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#2F5A35",
          muted: "#5F7D5C",
          accent: "#96A78D",
          light: "#B6CEB4",
          pale: "#EEF7EC",
          surface: "#F8FCF7",
        },
      },
    },
  },
  plugins: [],
}
