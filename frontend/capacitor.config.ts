import type { CapacitorConfig } from "@capacitor/cli";

// Android shell around the Vite build (dist/). See README "Run it on Android".
const config: CapacitorConfig = {
  appId: "com.juancardenas.pixelpomodoro",
  appName: "Pixel Pomodoro",
  webDir: "dist",
  backgroundColor: "#000000",
};

export default config;
