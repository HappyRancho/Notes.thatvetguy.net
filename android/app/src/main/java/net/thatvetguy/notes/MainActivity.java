package net.thatvetguy.notes;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.res.Configuration;
import android.net.Uri;
import android.net.http.SslError;
import android.os.Build;
import android.os.Bundle;
import android.os.Message;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.webkit.CookieManager;
import android.webkit.PermissionRequest;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.SslErrorHandler;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public final class MainActivity extends Activity {
    private FrameLayout root;
    private WebView webView;
    private ProgressBar progress;
    private ScrollView connectionPanel;
    private TextView connectionMessage;
    private String lastInternalUrl = LinkPolicy.HOME;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        root = new FrameLayout(this);
        root.setId(R.id.app_root);
        root.setBackgroundColor(getColor(R.color.app_background));
        setContentView(root);
        configureInsets();
        createWebView();
        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progress.setMax(100);
        root.addView(progress, new FrameLayout.LayoutParams(-1, dp(2), Gravity.TOP));
        createConnectionPanel();
        if (Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(0, this::handleBack);
        }
        if (state != null) {
            String saved = state.getString("internal_url");
            if (LinkPolicy.classify(saved) == LinkPolicy.Destination.INTERNAL) lastInternalUrl = saved;
            if (webView.restoreState(state) != null) return;
        }
        openInternal(lastInternalUrl);
    }

    @SuppressWarnings("deprecation")
    private void configureInsets() {
        boolean dark = (getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
        if (Build.VERSION.SDK_INT >= 30) {
            getWindow().setDecorFitsSystemWindows(false);
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) controller.setSystemBarsAppearance(
                    dark ? 0 : WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS,
                    WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS);
        } else {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    | (dark ? 0 : View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR));
        }
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets safe = insets.getInsets(WindowInsets.Type.systemBars()
                        | WindowInsets.Type.displayCutout() | WindowInsets.Type.ime());
                view.setPadding(safe.left, safe.top, safe.right, safe.bottom);
                return WindowInsets.CONSUMED;
            }
            view.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
                    insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
        });
        root.requestApplyInsets();
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void createWebView() {
        webView = new WebView(this);
        webView.setId(R.id.web_view);
        webView.setBackgroundColor(getColor(R.color.app_background));
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSafeBrowsingEnabled(true);
        settings.setGeolocationEnabled(false);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setSupportMultipleWindows(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setUserAgentString(settings.getUserAgentString() + " RxNotesAndroid/" + BuildConfig.VERSION_NAME);
        if (Build.VERSION.SDK_INT >= 33) settings.setAlgorithmicDarkeningAllowed(false);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, false);
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG);
        webView.setWebViewClient(new NotesClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override public void onProgressChanged(WebView view, int value) {
                if (progress == null || connectionPanel == null) return;
                progress.setProgress(value);
                progress.setVisibility(value < 100 && connectionPanel.getVisibility() != View.VISIBLE ? View.VISIBLE : View.GONE);
            }
            @Override public void onPermissionRequest(PermissionRequest request) { request.deny(); }
            @Override public boolean onCreateWindow(WebView view, boolean dialog, boolean gesture, Message result) {
                if (!gesture) return false;
                WebView popup = new WebView(MainActivity.this);
                popup.setWebViewClient(new WebViewClient() {
                    private boolean handled;
                    private void route(String url) {
                        if (handled || "about:blank".equals(url)) return;
                        handled = true;
                        routeFromPage(url, true);
                        popup.post(popup::destroy);
                    }
                    @Override public boolean shouldOverrideUrlLoading(WebView child, WebResourceRequest request) {
                        route(request.getUrl().toString());
                        return true;
                    }
                    @Override public void onPageStarted(WebView child, String url, android.graphics.Bitmap icon) { route(url); }
                });
                ((WebView.WebViewTransport) result.obj).setWebView(popup);
                result.sendToTarget();
                return true;
            }
        });
        webView.setDownloadListener((url, agent, disposition, mime, length) -> openExternal(url));
        root.addView(webView, 0, new FrameLayout.LayoutParams(-1, -1));
    }

    private final class NotesClient extends WebViewClient {
        @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            return request.isForMainFrame() && routeFromPage(request.getUrl().toString(), false);
        }
        @Override public void onPageStarted(WebView view, String url, android.graphics.Bitmap icon) {
            if (LinkPolicy.classify(url) == LinkPolicy.Destination.INTERNAL) lastInternalUrl = url;
            if (connectionPanel != null) connectionPanel.setVisibility(View.GONE);
        }
        @Override public void onPageFinished(WebView view, String url) {
            if (LinkPolicy.classify(url) != LinkPolicy.Destination.INTERNAL) return;
            view.evaluateJavascript("(function(){const m=document.querySelector('#more-sheet');"
                    + "if(!m||document.querySelector('#rx-android-refresh'))return;"
                    + "const row=document.createElement('div');row.id='rx-android-refresh';"
                    + "row.className='rx-theme-option notice-settings';"
                    + "const label=document.createElement('span');label.textContent='Refresh page';"
                    + "const small=document.createElement('small');small.textContent='Load the latest content';label.append(small);"
                    + "const button=document.createElement('button');button.type='button';button.textContent='Refresh';"
                    + "button.addEventListener('click',()=>location.reload());row.append(label,button);m.append(row);})()", null);
        }
        @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            if (request.isForMainFrame()) showConnectionError(getString(R.string.connection_message));
        }
        @Override public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse response) {
            if (request.isForMainFrame() && (response.getStatusCode() >= 500 || response.getStatusCode() == 403)) {
                showConnectionError(getString(R.string.http_error));
            }
        }
        @Override public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
            handler.cancel();
            if (error.getUrl().equals(view.getUrl())) showConnectionError(getString(R.string.secure_error));
        }
        @Override public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
            root.removeView(view);
            view.destroy();
            createWebView();
            showConnectionError(getString(R.string.connection_message));
            return true;
        }
    }

    private boolean routeFromPage(String value, boolean popup) {
        LinkPolicy.Destination destination = LinkPolicy.classify(value);
        if (destination == LinkPolicy.Destination.INTERNAL) {
            if (popup) openInternal(value);
            return popup;
        }
        openExternal(value);
        return true;
    }

    private void openInternal(String value) {
        if (LinkPolicy.classify(value) != LinkPolicy.Destination.INTERNAL) return;
        lastInternalUrl = value;
        connectionPanel.setVisibility(View.GONE);
        webView.loadUrl(value);
    }

    private void openExternal(String value) {
        LinkPolicy.Destination destination = LinkPolicy.classify(value);
        if (destination == LinkPolicy.Destination.BLOCKED) {
            Toast.makeText(this, R.string.unsupported_link, Toast.LENGTH_SHORT).show();
            return;
        }
        Intent intent = new Intent(destination == LinkPolicy.Destination.EMAIL ? Intent.ACTION_SENDTO
                : destination == LinkPolicy.Destination.PHONE ? Intent.ACTION_DIAL : Intent.ACTION_VIEW, Uri.parse(value));
        if (destination == LinkPolicy.Destination.BROWSER || destination == LinkPolicy.Destination.INTERNAL) intent.addCategory(Intent.CATEGORY_BROWSABLE);
        try { startActivity(intent); }
        catch (ActivityNotFoundException | SecurityException ignored) { Toast.makeText(this, R.string.no_handler, Toast.LENGTH_LONG).show(); }
    }

    @SuppressWarnings("deprecation")
    @Override public void onBackPressed() { handleBack(); }

    private void handleBack() {
        webView.evaluateJavascript("(function(){const d=document.querySelector('dialog[open]');if(!d)return false;"
                + "const b=d.querySelector('[data-close]');if(b)b.click();else document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));"
                + "if(d.open)d.close();return true;})()", closed -> {
            if (isFinishing() || isDestroyed()) return;
            if ("true".equals(closed)) return;
            if (webView.canGoBack()) { connectionPanel.setVisibility(View.GONE); webView.goBack(); }
            else finish();
        });
    }

    private void createConnectionPanel() {
        connectionPanel = new ScrollView(this);
        connectionPanel.setId(R.id.connection_panel);
        connectionPanel.setFillViewport(true);
        connectionPanel.setBackgroundColor(getColor(R.color.app_background));
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER);
        content.setPadding(dp(28), dp(24), dp(28), dp(24));
        ImageView logo = new ImageView(this);
        logo.setImageResource(R.drawable.ic_launcher);
        logo.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        content.addView(logo, new LinearLayout.LayoutParams(dp(76), dp(76)));
        TextView title = new TextView(this);
        title.setText(R.string.connection_title);
        title.setTextSize(25);
        title.setTextColor(getColor(R.color.app_text));
        title.setGravity(Gravity.CENTER);
        title.setPadding(0, dp(22), 0, dp(10));
        content.addView(title);
        connectionMessage = new TextView(this);
        connectionMessage.setTextSize(16);
        connectionMessage.setTextColor(getColor(R.color.app_muted));
        connectionMessage.setGravity(Gravity.CENTER);
        connectionMessage.setPadding(0, 0, 0, dp(20));
        content.addView(connectionMessage);
        Button retry = new Button(this);
        retry.setId(R.id.retry_button);
        retry.setText(R.string.retry);
        retry.setAllCaps(false);
        retry.setMinHeight(dp(48));
        retry.setOnClickListener(view -> openInternal(lastInternalUrl));
        content.addView(retry, new LinearLayout.LayoutParams(-1, -2));
        Button browser = new Button(this);
        browser.setText(R.string.open_browser);
        browser.setAllCaps(false);
        browser.setMinHeight(dp(48));
        browser.setOnClickListener(view -> openExternal(lastInternalUrl));
        content.addView(browser, new LinearLayout.LayoutParams(-1, -2));
        connectionPanel.addView(content, new ScrollView.LayoutParams(-1, -1));
        root.addView(connectionPanel, new FrameLayout.LayoutParams(-1, -1));
        connectionPanel.setVisibility(View.GONE);
    }

    private void showConnectionError(String message) {
        if (isFinishing() || isDestroyed()) return;
        progress.setVisibility(View.GONE);
        connectionMessage.setText(message);
        connectionPanel.setVisibility(View.VISIBLE);
    }

    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    @Override protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        outState.putString("internal_url", lastInternalUrl);
        super.onSaveInstanceState(outState);
    }
    @Override public void onConfigurationChanged(Configuration config) { super.onConfigurationChanged(config); root.requestApplyInsets(); }
    @Override protected void onResume() { super.onResume(); if (webView != null) webView.onResume(); }
    @Override protected void onPause() { if (webView != null) webView.onPause(); super.onPause(); }
    @Override protected void onDestroy() {
        if (webView != null) { root.removeView(webView); webView.destroy(); }
        super.onDestroy();
    }
}
