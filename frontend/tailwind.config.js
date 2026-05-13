/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Instrument Serif"', "serif"],
        sans:  ["Geist", "system-ui", "sans-serif"],
        mono:  ['"JetBrains Mono"', "monospace"],
      },
      colors: {
        accent: {
          DEFAULT: "#5EEAD4",
          dim:     "#5EEAD422",
          glow:    "#5EEAD4",
        },
      },
      animation: {
        "fade-up":   "fadeUp 0.35s ease-out both",
        "pulse-ring": "pulseRing 2s infinite",
        "bounce-dot": "bounceDot 1.4s ease-in-out infinite",
      },
      keyframes: {
        fadeUp:    { from: { opacity: 0, transform: "translateY(6px)" }, to: { opacity: 1, transform: "translateY(0)" } },
        pulseRing: {
          "0%":   { boxShadow: "0 0 0 0 rgba(94,234,212,0.4)" },
          "70%":  { boxShadow: "0 0 0 10px rgba(94,234,212,0)" },
          "100%": { boxShadow: "0 0 0 0 rgba(94,234,212,0)" },
        },
        bounceDot: {
          "0%,80%,100%": { transform: "scale(0.6)", opacity: 0.5 },
          "40%":         { transform: "scale(1)",   opacity: 1   },
        },
      },
    },
  },
  plugins: [],
};
