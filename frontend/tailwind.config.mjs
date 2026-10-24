/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        "navy": "#0d1b36",
        "amber": {
                "DEFAULT": "#e2b155",
                "50": "#fdf6e7",
                "100": "#faedb2",
                "200": "#f5e089",
                "300": "#eecb5f",
                "600": "#c98d2b",
                "900": "#3c2a07"
        }
},
      fontFamily: {
        "display": [
                "'Cormorant Garamond'",
                "Georgia",
                "serif"
        ],
        "body": [
                "'Inter'",
                "system-ui",
                "sans-serif"
        ],
        "mono": [
                "'JetBrains Mono'",
                "ui-monospace",
                "monospace"
        ]
},
    },
  },
  plugins: [],
};
