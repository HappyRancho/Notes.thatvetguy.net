Rx Notes for Android — direct-install live-site app

App: net.thatvetguy.notes
Version: 0.1.0 (1)
Minimum Android: 8.0 (API 26)
Compile / target: Android 16 (API 36)

The app loads https://notes.thatvetguy.net/ and keeps website updates automatic.
No browser toolbar or second app navigation bar is added. Existing notes,
books, support, theme preferences and saved checklists remain website features.

Android-specific behavior:
- The More menu adds Refresh page for checking the latest website content.
- Native back closes website dialogs before navigating page history or exiting.
- System bars, cutouts and the keyboard have native window insets.
- Rotation retains the active WebView and unsent form fields.
- Google Drive, PDFs, Telegram and other external links open in phone apps/browser.
- Email drafts use the phone's mail app. Screenshots are attached there.
- A native retry screen handles main-page connection failures.
- Only INTERNET permission is requested; no storage, camera or contacts permission.
- Only the exact HTTPS notes origin stays in the WebView. File access, mixed
  content, third-party cookies and native JavaScript bridges are disabled.
- Release code/resources are optimized; no third-party runtime SDK is bundled.

Build with JDK 17 and Android SDK 36:
  ./gradlew testDebugUnitTest lintDebug assembleRelease

Without signing environment variables, release output is unsigned. For a signed
build set RX_NOTES_KEYSTORE and RX_NOTES_KEYSTORE_PASSWORD. The alias is rx-notes.
Keep signing material outside Git. Reuse the same key for future APK updates.
The Gradle wrapper and distribution are pinned and checksum verified.

The Android APK workflow builds unsigned release/debug APKs, runs routing tests,
Android lint and Android 15 emulator checks. APK signing is a separate local step;
no signing key is stored in source or CI artifacts. This workflow does not submit
anything to Google Play or publish a public release.

This live-site app needs internet access. An offline book collection is not bundled.
