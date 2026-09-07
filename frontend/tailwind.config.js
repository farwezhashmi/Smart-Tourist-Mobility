/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17221f",
        moss: "#486a5a",
        saffron: "#e99c46",
        paper: "#f4f0e6",
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        sans: ["Trebuchet MS", "sans-serif"],
      },
    },
  },
  plugins: [],
};
