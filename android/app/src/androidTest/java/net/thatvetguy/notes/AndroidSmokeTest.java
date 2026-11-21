package net.thatvetguy.notes;

import android.app.Instrumentation;
import android.animation.ValueAnimator;
import android.content.pm.ActivityInfo;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.net.Uri;
import android.view.View;
import android.webkit.WebResourceResponse;
import java.io.ByteArrayInputStream;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.ProgressBar;
import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import java.io.File;
import java.io.FileOutputStream;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public class AndroidSmokeTest {
    private final Instrumentation instrumentation = InstrumentationRegistry.getInstrumentation();

    private String js(ActivityScenario<MainActivity> scenario, String script) throws Exception {
        CountDownLatch latch = new CountDownLatch(1);
        AtomicReference<String> result = new AtomicReference<>();
        scenario.onActivity(activity -> ((WebView) activity.findViewById(R.id.web_view)).evaluateJavascript(script, value -> { result.set(value); latch.countDown(); }));
        assertTrue("WebView response timed out", latch.await(5, TimeUnit.SECONDS));
        return result.get();
    }
    private void waitFor(ActivityScenario<MainActivity> scenario, String expression) throws Exception {
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(45);
        while (System.nanoTime() < deadline) {
            if ("true".equals(js(scenario, expression))) return;
            Thread.sleep(200);
        }
        fail("Timed out: " + expression);
    }

    @Test public void liveWebsiteHasNativeInsetsAndCanNavigateBack() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            waitFor(scenario, "document.documentElement.dataset.ui==='rx' && !!document.querySelector('h1')");
            scenario.onActivity(activity -> {
                WebView web = activity.findViewById(R.id.web_view);
                assertTrue(web.getSettings().getJavaScriptEnabled());
                assertTrue(web.getSettings().getDomStorageEnabled());
                assertFalse(web.getSettings().getAllowFileAccess());
                assertFalse(web.getSettings().getAllowContentAccess());
                assertEquals(WebSettings.MIXED_CONTENT_NEVER_ALLOW, web.getSettings().getMixedContentMode());
                assertTrue(activity.findViewById(R.id.app_root).getPaddingTop() > 0);
            });
            boolean dark = (instrumentation.getTargetContext().getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
            assertEquals(Boolean.toString(dark), js(scenario, "matchMedia('(prefers-color-scheme: dark)').matches"));
            waitFor(scenario, "!!document.querySelector('#rx-android-refresh')");
            scenario.onActivity(activity -> assertEquals(View.GONE, activity.findViewById(R.id.loading_indicator).getVisibility()));
            File shot = new File(instrumentation.getTargetContext().getExternalFilesDir(null), dark ? "rx-notes-home-dark.png" : "rx-notes-home-light.png");
            try (FileOutputStream out = new FileOutputStream(shot)) { instrumentation.getUiAutomation().takeScreenshot().compress(Bitmap.CompressFormat.PNG, 100, out); }
            scenario.onActivity(activity -> ((WebView) activity.findViewById(R.id.web_view)).loadUrl(LinkPolicy.HOME + "books/"));
            waitFor(scenario, "location.pathname==='/books/' && !!document.querySelector('#books-query')");
            instrumentation.getUiAutomation().performGlobalAction(1);
            waitFor(scenario, "location.pathname==='/' && !!document.querySelector('#notes')");
        }
    }

    @Test public void nativeBackClosesWebDialogsAndRotationRetainsInputs() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                WebView web = activity.findViewById(R.id.web_view);
                web.stopLoading();
                web.loadDataWithBaseURL(LinkPolicy.HOME, "<html><body><input id='draft' value='Keep my draft'><dialog id='menu' open>More</dialog></body></html>", "text/html", "UTF-8", null);
            });
            waitFor(scenario, "!!document.querySelector('#menu[open]')");
            instrumentation.getUiAutomation().performGlobalAction(1);
            waitFor(scenario, "!!document.querySelector('#menu:not([open])')");
            scenario.onActivity(activity -> activity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE));
            waitFor(scenario, "innerWidth>innerHeight && document.querySelector('#draft').value==='Keep my draft'");
        }
    }

    @Test public void mainFrameServerFailureShowsUsableRetry() {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                WebView web = activity.findViewById(R.id.web_view);
                web.stopLoading();
                WebResourceRequest request = new WebResourceRequest() {
                    public Uri getUrl() { return Uri.parse(LinkPolicy.HOME); }
                    public boolean isForMainFrame() { return true; }
                    public boolean isRedirect() { return false; }
                    public boolean hasGesture() { return false; }
                    public String getMethod() { return "GET"; }
                    public Map<String,String> getRequestHeaders() { return Collections.emptyMap(); }
                };
                web.getWebViewClient().onReceivedHttpError(web, request,
                        new WebResourceResponse("text/html", "UTF-8", 503, "Service Unavailable",
                                Collections.emptyMap(), new ByteArrayInputStream(new byte[0])));
                assertEquals(View.VISIBLE, activity.findViewById(R.id.connection_panel).getVisibility());
                assertTrue(activity.findViewById(R.id.retry_button).isEnabled());
                assertEquals(View.GONE, activity.findViewById(R.id.loading_indicator).getVisibility());
            });
        }
    }

    @Test public void loadingShowsRealProgressAndEndsAtFirstVisibleContent() {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                WebView web = activity.findViewById(R.id.web_view);
                web.stopLoading();
                web.getWebViewClient().onPageStarted(web, LinkPolicy.HOME, null);
                web.getWebChromeClient().onProgressChanged(web, 37);
                assertEquals(View.VISIBLE, activity.findViewById(R.id.loading_indicator).getVisibility());
                assertEquals(37, ((ProgressBar) activity.findViewById(R.id.loading_progress)).getProgress());
                web.getWebViewClient().onPageCommitVisible(web, LinkPolicy.HOME);
                assertEquals(View.GONE, activity.findViewById(R.id.loading_indicator).getVisibility());
                web.getWebViewClient().onPageStarted(web, LinkPolicy.HOME + "books/", null);
                assertEquals(View.VISIBLE, activity.findViewById(R.id.loading_indicator).getVisibility());
                assertEquals(View.GONE, activity.findViewById(R.id.startup_panel).getVisibility());
                web.getWebViewClient().onPageFinished(web, LinkPolicy.HOME + "books/");
                assertEquals(View.GONE, activity.findViewById(R.id.loading_indicator).getVisibility());
            });
        }
    }

    @Test public void loadingPulseRespectsMotionSettingAndStopsWhenHidden() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                activity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
                WebView web = activity.findViewById(R.id.web_view);
                web.stopLoading();
                web.loadDataWithBaseURL(LinkPolicy.HOME, "<html><head><meta name='viewport' content='width=device-width,initial-scale=1'></head><body id='motion-fixture'>Motion fixture</body></html>", "text/html", "UTF-8", null);
            });
            waitFor(scenario, "!!document.querySelector('#motion-fixture') && document.readyState==='complete' && innerWidth<innerHeight");
            instrumentation.waitForIdleSync();
            scenario.onActivity(activity -> {
                BrandLoadingView loading = activity.findViewById(R.id.loading_indicator);
                loading.show(true);
                loading.updateProgress(37);
            });
            if (ValueAnimator.areAnimatorsEnabled()) {
                AtomicReference<Float> alpha = new AtomicReference<>(1f);
                long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(3);
                do {
                    Thread.sleep(100);
                    scenario.onActivity(activity -> alpha.set(activity.findViewById(R.id.loading_logo).getAlpha()));
                } while (alpha.get() >= .98f && System.nanoTime() < deadline);
                assertTrue("Loading logo should pulse gently", alpha.get() >= .64f && alpha.get() < .98f);
            } else {
                scenario.onActivity(activity -> assertEquals(1f, activity.findViewById(R.id.loading_logo).getAlpha(), .001f));
            }
            boolean dark = (instrumentation.getTargetContext().getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
            File shot = new File(instrumentation.getTargetContext().getExternalFilesDir(null), dark ? "rx-notes-startup-dark.png" : "rx-notes-startup-light.png");
            try (FileOutputStream out = new FileOutputStream(shot)) { instrumentation.getUiAutomation().takeScreenshot().compress(Bitmap.CompressFormat.PNG, 100, out); }
            scenario.onActivity(activity -> {
                BrandLoadingView loading = activity.findViewById(R.id.loading_indicator);
                loading.setPaused(true);
                assertEquals(1f, activity.findViewById(R.id.loading_logo).getAlpha(), .001f);
                loading.hide();
                assertEquals(View.GONE, loading.getVisibility());
            });
        }
    }
}
