package net.thatvetguy.notes;

import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

/** A gentle pulse while a main page loads; never delays a page becoming visible. */
final class BrandLoadingView extends FrameLayout {
    private final LinearLayout startup;
    private final LinearLayout compact;
    private final ImageView startupLogo;
    private final ImageView compactLogo;
    private final TextView startupStatus;
    private final TextView compactStatus;
    private final ProgressBar meter;
    private ObjectAnimator pulse;
    private boolean initial;
    private boolean paused;

    BrandLoadingView(Context context) {
        super(context);
        setId(R.id.loading_indicator);
        startup = new LinearLayout(context);
        startup.setId(R.id.startup_panel);
        startup.setOrientation(LinearLayout.VERTICAL);
        startup.setGravity(Gravity.CENTER);
        startup.setBackgroundColor(context.getColor(R.color.app_background));
        startup.setClickable(true);
        startupLogo = logo(260, 116);
        startupLogo.setId(R.id.loading_logo);
        startup.addView(startupLogo);
        startupStatus = status();
        startupStatus.setPadding(0, dp(14), 0, dp(14));
        startup.addView(startupStatus);
        meter = new ProgressBar(context, null, android.R.attr.progressBarStyleHorizontal);
        meter.setId(R.id.loading_progress);
        meter.setMax(100);
        meter.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        startup.addView(meter, new LinearLayout.LayoutParams(dp(160), dp(3)));
        addView(startup, new FrameLayout.LayoutParams(-1, -1));

        compact = new LinearLayout(context);
        compact.setOrientation(LinearLayout.HORIZONTAL);
        compact.setGravity(Gravity.CENTER);
        compact.setPadding(dp(8), dp(2), dp(12), dp(2));
        GradientDrawable card = new GradientDrawable();
        card.setColor(context.getColor(R.color.app_background));
        card.setCornerRadius(dp(12));
        compact.setBackground(card);
        compact.setElevation(dp(4));
        compactLogo = logo(90, 40);
        compact.addView(compactLogo);
        compactStatus = status();
        compactStatus.setTextSize(12);
        compactStatus.setPadding(dp(6), 0, 0, 0);
        compact.addView(compactStatus);
        FrameLayout.LayoutParams chip = new FrameLayout.LayoutParams(-2, dp(44), Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        chip.topMargin = dp(6);
        addView(compact, chip);
        setVisibility(GONE);
    }

    private ImageView logo(int width, int height) {
        ImageView image = new ImageView(getContext());
        image.setImageResource(R.drawable.ic_wordmark);
        image.setScaleType(ImageView.ScaleType.FIT_CENTER);
        image.setContentDescription(getContext().getString(R.string.app_name));
        image.setLayoutParams(new LinearLayout.LayoutParams(dp(width), dp(height)));
        return image;
    }
    private TextView status() {
        TextView text = new TextView(getContext());
        text.setTextSize(13);
        text.setTextColor(getContext().getColor(R.color.app_muted));
        text.setGravity(Gravity.CENTER);
        return text;
    }
    void show(boolean firstPage) {
        stopPulse();
        initial = firstPage;
        startup.setVisibility(firstPage ? VISIBLE : GONE);
        compact.setVisibility(firstPage ? GONE : VISIBLE);
        updateProgress(0);
        setVisibility(VISIBLE);
        startPulse();
    }
    void updateProgress(int value) {
        int percent = Math.max(0, Math.min(100, value));
        meter.setProgress(percent);
        startupStatus.setText(getContext().getString(R.string.startup_loading, percent));
        compactStatus.setText(getContext().getString(R.string.page_loading, percent));
    }
    void hide() { stopPulse(); setVisibility(GONE); }
    void setPaused(boolean value) {
        paused = value;
        if (value) stopPulse(); else startPulse();
    }
    private void startPulse() {
        if (pulse != null || paused || !isShown() || getWindowVisibility() != VISIBLE
                || !ValueAnimator.areAnimatorsEnabled()) return;
        ImageView target = initial ? startupLogo : compactLogo;
        pulse = ObjectAnimator.ofFloat(target, View.ALPHA, .65f, 1f);
        pulse.setDuration(900);
        pulse.setRepeatMode(ValueAnimator.REVERSE);
        pulse.setRepeatCount(ValueAnimator.INFINITE);
        pulse.start();
    }
    private void stopPulse() {
        if (pulse != null) { pulse.cancel(); pulse = null; }
        if (startupLogo != null) startupLogo.setAlpha(1f);
        if (compactLogo != null) compactLogo.setAlpha(1f);
    }
    @Override protected void onAttachedToWindow() { super.onAttachedToWindow(); startPulse(); }
    @Override protected void onWindowVisibilityChanged(int visibility) {
        super.onWindowVisibilityChanged(visibility);
        if (startupLogo == null) return;
        if (visibility == VISIBLE) startPulse(); else stopPulse();
    }
    @Override protected void onDetachedFromWindow() { stopPulse(); super.onDetachedFromWindow(); }
    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
}
