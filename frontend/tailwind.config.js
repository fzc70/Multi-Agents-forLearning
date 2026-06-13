/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        muted: "#64748B",
        line: "#E4E9F1",
        canvas: "#F4F6F3"
      },
      borderRadius: {
        ui: "8px"
      },
      boxShadow: {
        soft: "0 18px 48px rgba(20, 35, 70, 0.08)"
      }
    }
  },
  plugins: []
};
