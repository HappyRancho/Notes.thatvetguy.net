#!/usr/bin/env bash
# Keep emulator evidence even when a device test fails.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p ../android-qa
./gradlew --no-daemon connectedDebugAndroidTest
result=$?
if [ "$result" -eq 0 ]; then
  adb shell cmd uimode night yes
  adb shell am force-stop net.thatvetguy.notes.debug
  ./gradlew --no-daemon connectedDebugAndroidTest '-Pandroid.testInstrumentationRunnerArguments.class=net.thatvetguy.notes.AndroidSmokeTest#liveWebsiteHasNativeInsetsAndCanNavigateBack'
  result=$?
fi
adb pull /sdcard/Android/data/net.thatvetguy.notes.debug/files/ ../android-qa/ || true
adb exec-out screencap -p > ../android-qa/final-screen.png || true
adb logcat -d -s AndroidRuntime > ../android-qa/runtime.log || true
exit "$result"
