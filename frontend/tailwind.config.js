/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      // ── Institutional Intelligence Design System ──────────────────────────
      colors: {
        // Surfaces
        "surface":                   "#f7f9fb",
        "surface-dim":               "#d8dadc",
        "surface-bright":            "#f7f9fb",
        "surface-container-lowest":  "#ffffff",
        "surface-container-low":     "#f2f4f6",
        "surface-container":         "#eceef0",
        "surface-container-high":    "#e6e8ea",
        "surface-container-highest": "#e0e3e5",
        "surface-variant":           "#e0e3e5",
        "surface-tint":              "#565e74",
        // On-surfaces
        "on-surface":                "#191c1e",
        "on-surface-variant":        "#45464d",
        "inverse-surface":           "#2d3133",
        "inverse-on-surface":        "#eff1f3",
        // Outlines
        "outline":                   "#76777d",
        "outline-variant":           "#c6c6cd",
        // Primary – Ink Black
        "primary":                   "#000000",
        "on-primary":                "#ffffff",
        "primary-container":         "#131b2e",
        "on-primary-container":      "#7c839b",
        "inverse-primary":           "#bec6e0",
        "primary-fixed":             "#dae2fd",
        "primary-fixed-dim":         "#bec6e0",
        "on-primary-fixed":          "#131b2e",
        "on-primary-fixed-variant":  "#3f465c",
        // Secondary – Electric Indigo
        "secondary":                 "#4648d4",
        "on-secondary":              "#ffffff",
        "secondary-container":       "#6063ee",
        "on-secondary-container":    "#fffbff",
        "secondary-fixed":           "#e1e0ff",
        "secondary-fixed-dim":       "#c0c1ff",
        "on-secondary-fixed":        "#07006c",
        "on-secondary-fixed-variant":"#2f2ebe",
        // Tertiary – Sage Green
        "tertiary":                  "#000000",
        "on-tertiary":               "#ffffff",
        "tertiary-container":        "#002113",
        "on-tertiary-container":     "#009668",
        "tertiary-fixed":            "#6ffbbe",
        "tertiary-fixed-dim":        "#4edea3",
        "on-tertiary-fixed":         "#002113",
        "on-tertiary-fixed-variant": "#005236",
        // Error
        "error":                     "#ba1a1a",
        "on-error":                  "#ffffff",
        "error-container":           "#ffdad6",
        "on-error-container":        "#93000a",
        // Background
        "background":                "#f7f9fb",
        "on-background":             "#191c1e",
      },
      // ── Typography ────────────────────────────────────────────────────────
      fontFamily: {
        "display-lg":          ["Newsreader", "Georgia", "serif"],
        "headline-lg":         ["Newsreader", "Georgia", "serif"],
        "headline-lg-mobile":  ["Newsreader", "Georgia", "serif"],
        "editorial-body":      ["Newsreader", "Georgia", "serif"],
        "interface-md":        ["Geist", "Inter", "system-ui", "sans-serif"],
        "interface-sm":        ["Geist", "Inter", "system-ui", "sans-serif"],
        "label-caps":          ["Geist", "Inter", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-lg":         ["48px", { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "600" }],
        "headline-lg":        ["32px", { lineHeight: "1.2", fontWeight: "500" }],
        "headline-lg-mobile": ["24px", { lineHeight: "1.2", fontWeight: "500" }],
        "editorial-body":     ["20px", { lineHeight: "1.6", fontWeight: "400" }],
        "interface-md":       ["16px", { lineHeight: "1.5", fontWeight: "400" }],
        "interface-sm":       ["14px", { lineHeight: "1.4", fontWeight: "500" }],
        "label-caps":         ["12px", { lineHeight: "1",   letterSpacing: "0.05em", fontWeight: "600" }],
      },
      // ── Border Radius ─────────────────────────────────────────────────────
      borderRadius: {
        "sm":      "0.25rem",  // 4px
        "DEFAULT": "0.5rem",   // 8px — standard
        "md":      "0.75rem",  // 12px
        "lg":      "1rem",     // 16px — large containers
        "xl":      "1.5rem",   // 24px
        "full":    "9999px",
      },
      // ── Spacing ───────────────────────────────────────────────────────────
      spacing: {
        "unit":           "4px",
        "gutter":         "24px",
        "margin-mobile":  "16px",
        "margin-desktop": "48px",
        "container-max":  "1280px",
      },
      // ── Box Shadow ────────────────────────────────────────────────────────
      boxShadow: {
        "card":    "0 4px 20px rgba(15, 23, 42, 0.04)",
        "overlay": "0 8px 32px rgba(15, 23, 42, 0.08)",
        "focus":   "0 0 0 3px rgba(70, 72, 212, 0.15)",
      },
      // ── Animation ─────────────────────────────────────────────────────────
      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
        "spin-slow": {
          from: { transform: "rotate(0deg)" },
          to:   { transform: "rotate(360deg)" },
        },
      },
      animation: {
        "fade-in":  "fade-in 0.25s ease-out",
        "spin-slow": "spin-slow 1.2s linear infinite",
      },
      // ── Max-width helper ──────────────────────────────────────────────────
      maxWidth: {
        "container": "1280px",
      },
    },
  },
  plugins: [],
}
