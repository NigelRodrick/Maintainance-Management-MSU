# MSU Maintenance — mobile shell (Android + iOS)

This folder is a **[Capacitor](https://capacitorjs.com/)** wrapper: it runs your **already-deployed** Flask web app inside a native WebView. It is not a rewrite of the server; you must host the Flask app on the internet (HTTPS) first.

## Automated setup (recommended)

From the `mobile/` folder:

```bash
npm run setup
```

Or **Windows**: double-click **`Setup-All.bat`**. Or **macOS/Linux**: `chmod +x setup-all.sh && ./setup-all.sh`

This runs `npm install`, `cap add android` (and `cap add ios` on macOS only), and `cap sync`.

**GitHub Actions** (on push to `main` when `mobile/**` changes):

- **Mobile Android APK (debug)** — builds a debug APK and uploads an artifact.
- **Mobile iOS project sync** — on **macOS**, generates `ios/` and runs `cap sync` (no signed IPA; use Xcode locally for release).

## Prerequisites

| Platform | You need |
|----------|----------|
| **All** | [Node.js 18+](https://nodejs.org/), npm |
| **Android** | [Android Studio](https://developer.android.com/studio) (SDK, build tools) |
| **iOS** | **macOS** + [Xcode](https://developer.apple.com/xcode/) + Apple Developer account for device/TestFlight |

## 1. Point the app at your live URL

Edit `capacitor.config.json` and replace the placeholder:

```json
"server": {
  "url": "https://your-app.onrender.com",
  "cleartext": false
}
```

- Use **HTTPS** in production (required for iOS App Transport Security unless you add exceptions).
- For **HTTP** dev-only testing, set `"cleartext": true` and adjust iOS ATS (see Capacitor docs).

## 2. Install and add native projects

From the `mobile/` directory:

```bash
npm install
npx cap add android
npx cap add ios
npx cap sync
```

This creates `android/` and `ios/` (not committed by default; regenerate with `cap add` on a new machine).

## 3. Build Android (APK / AAB)

```bash
npx cap open android
```

In Android Studio: **Build → Build Bundle(s) / APK(s)** (or use Gradle for release signing).

- Release builds need a **keystore** and signing config in the Android project.

## 4. Build iOS

```bash
npx cap open ios
```

In Xcode: select your **Team**, set a **unique bundle ID** if needed, then **Product → Archive** for distribution (TestFlight / App Store) or run on a simulator.

## 5. Sync after config changes

Whenever you change `capacitor.config.json`:

```bash
npx cap sync
```

## Notes

- **Cookies / login**: Same as a browser; ensure your server sets cookies suitable for your domain and `SameSite` as needed.
- **CORS**: Not an issue for WebView same-origin to `server.url` when configured as above.
- **Offline**: This shell does not run Flask on the device; offline mode would require a different architecture.
