/**
 * Android-only behavior (Capacitor): keep the screen on while the timer runs,
 * play the 8-bit chime at phase end even when the app is hidden, and route the
 * system back button. Everything here is a no-op in the browser and in pywebview.
 */

import { KeepAwake } from "@capacitor-community/keep-awake";
import { App } from "@capacitor/app";
import { LocalNotifications, type Channel } from "@capacitor/local-notifications";

import { isNative } from "./local";
import type { Phase, PomodoroTimer } from "./timer";

const ALARM_ID = 1;

// Channel sound is fixed once created on Android 8+; bump the suffix if a WAV changes.
// res/raw/chime_*.wav are rendered from sound.ts by `python -m pomodoro --export-chimes`.
const CHANNELS: Channel[] = [
  { id: "phase-end-break-v1", name: "Focus finished", sound: "chime_break.wav", importance: 4, vibration: true },
  { id: "phase-end-work-v1", name: "Break finished", sound: "chime_work.wav", importance: 4, vibration: true },
  { id: "phase-end-silent-v1", name: "Phase finished (sound off)", importance: 2, vibration: false },
];

const MESSAGE: Record<Phase, { title: string; body: string; channelId: string }> = {
  work: { title: "Focus done", body: "Take a break.", channelId: "phase-end-break-v1" },
  short: { title: "Break over", body: "Back to work.", channelId: "phase-end-work-v1" },
  long: { title: "Long break over", body: "Back to work.", channelId: "phase-end-work-v1" },
};

export interface AndroidHooks {
  timer: PomodoroTimer;
  soundOn: () => boolean;
  /** Close an open panel; returns false if none was open. */
  closePanel: () => boolean;
}

export class AndroidShell {
  private awake = false;
  private alarmAt: number | null = null;
  private muteUntil = 0;

  private constructor(private hooks: AndroidHooks) {}

  static async setup(hooks: AndroidHooks): Promise<AndroidShell | null> {
    if (!isNative()) return null;
    const shell = new AndroidShell(hooks);
    await App.addListener("pause", () => void shell.onHidden());
    await App.addListener("resume", () => void shell.onVisible());
    await App.addListener("backButton", () => {
      if (!hooks.closePanel()) void App.minimizeApp();
    });
    try {
      for (const channel of CHANNELS) await LocalNotifications.createChannel(channel);
      await LocalNotifications.requestPermissions();
    } catch (err) {
      console.warn("notifications unavailable", err);
    }
    return shell;
  }

  /** Call every frame: holds a wake lock only while the timer is running. */
  sync(): void {
    const running = this.hooks.timer.status === "running";
    if (running === this.awake) return;
    this.awake = running;
    void (running ? KeepAwake.keepAwake() : KeepAwake.allowSleep()).catch(() => {});
  }

  /**
   * True if the phase-end chime already played as a notification while hidden.
   * main.ts asks before playing the WebAudio chime so it doesn't sound twice.
   */
  chimeAlreadyPlayed(): boolean {
    return Date.now() < this.muteUntil;
  }

  private async onHidden(): Promise<void> {
    const { timer } = this.hooks;
    if (timer.status !== "running") return;
    const at = Date.now() + timer.remainingMs();
    const msg = MESSAGE[timer.phase];
    // Exact alarms come from USE_EXACT_ALARM (manifest). If they are somehow denied,
    // go inexact instead of letting the plugin open Settings as the app goes away.
    const exact = await LocalNotifications.checkExactNotificationSetting()
      .then((s) => s.exact_alarm === "granted")
      .catch(() => false);
    try {
      await LocalNotifications.schedule({
        notifications: [
          {
            id: ALARM_ID,
            title: msg.title,
            body: msg.body,
            channelId: this.hooks.soundOn() ? msg.channelId : "phase-end-silent-v1",
            schedule: { at: new Date(at), allowWhileIdle: true },
            isExactNotification: exact,
          },
        ],
      });
      this.alarmAt = at;
    } catch (err) {
      console.warn("could not schedule phase-end alarm", err);
    }
  }

  private async onVisible(): Promise<void> {
    if (this.alarmAt === null) return;
    // The timer catches up on the next frame; if the alarm already fired, mute that catch-up chime.
    if (Date.now() >= this.alarmAt) this.muteUntil = Date.now() + 3000;
    this.alarmAt = null;
    await LocalNotifications.cancel({ notifications: [{ id: ALARM_ID }] }).catch(() => {});
  }
}
