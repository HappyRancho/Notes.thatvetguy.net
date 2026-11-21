package net.thatvetguy.notes;

import android.app.Instrumentation;
import android.content.pm.ActivityInfo;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.net.Uri;
import android.view.View;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
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

    @Test public void mainFrameNetworkFailureShowsUsableRetry() {
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
                web.getWebViewClient().onReceivedError(web, request, new WebResourceError() {
                    public int getErrorCode() { return -2; }
                    public CharSequence getDescription() { return "Network unavailable"; }
                });
                assertEquals(View.VISIBLE, activity.findViewById(R.id.connection_panel).getVisibility());
                assertTrue(activity.findViewById(R.id.retry_button).isEnabled());
            });
        }
    }
}
