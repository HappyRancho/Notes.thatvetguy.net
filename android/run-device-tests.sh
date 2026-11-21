#!/usr/bin/env bash
# Keep emulator evidence even when a device test fails.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p ../android-qa
# Test the new pulse with property animations enabled, then reduced motion below.
adb shell settings put global animator_duration_scale 1
./gradlew --no-daemon connectedDebugAndroidTest -Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true
result=$?
if [ "$result" -eq 0 ]; then
  adb shell settings put global animator_duration_scale 0
  adb shell cmd uimode night yes
  adb shell am force-stop net.thatvetguy.notes.debug
  ./gradlew --no-daemon connectedDebugAndroidTest -Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true '-Pandroid.testInstrumentationRunnerArguments.class=net.thatvetguy.notes.AndroidSmokeTest#liveWebsiteHasNativeInsetsAndCanNavigateBack,net.thatvetguy.notes.AndroidSmokeTest#loadingPulseRespectsMotionSettingAndStopsWhenHidden'
  result=$?
fi
adb pull /sdcard/Android/data/net.thatvetguy.notes.debug/files/ ../android-qa/ || true
adb exec-out screencap -p > ../android-qa/final-screen.png || true
adb logcat -d -s AndroidRuntime > ../android-qa/runtime.log || true
# Keep the startup preview available through logs as well as CI artifacts.
python3 - <<'PYVIEW'
from pathlib import Path
import base64, json
for name in ['rx-notes-startup-light.png', 'rx-notes-startup-dark.png']:
    file = next(Path('../android-qa').rglob(name), None)
    if file:
        print('ANDROID_BRAND_PREVIEW ' + json.dumps({'name': name, 'data': base64.b64encode(file.read_bytes()).decode()}))
PYVIEW
exit "$result"
