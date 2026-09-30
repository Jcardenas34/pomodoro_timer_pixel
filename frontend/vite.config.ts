import { defineConfig } from "vite";

export default defineConfig({
  // Relative paths so pywebview can load dist/index.html from disk.
  base: "./",
  server: { host: true, port: 5173, strictPort: true },
});
