// @ts-check
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

// Deployed to GitHub Pages at gordonwatts.github.io/iris-hep-llm-performance —
// `base` must match the repo name so every internal link (routed through
// src/lib/url.ts's `href()`) resolves under that path in production while
// still working at the site root in `astro dev`.
export default defineConfig({
  site: "https://gordonwatts.github.io",
  base: "/iris-hep-llm-performance",
  output: "static",
  vite: {
    plugins: [tailwindcss()],
  },
});
