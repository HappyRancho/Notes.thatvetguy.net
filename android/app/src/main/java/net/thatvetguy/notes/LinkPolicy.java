package net.thatvetguy.notes;

import java.net.URI;
import java.util.Locale;

/** Only the exact HTTPS notes origin belongs inside the app. */
final class LinkPolicy {
    static final String HOME = "https://notes.thatvetguy.net/";
    enum Destination { INTERNAL, BROWSER, EMAIL, PHONE, BLOCKED }

    static Destination classify(String value) {
        try {
            URI uri = new URI(value);
            String scheme = uri.getScheme();
            if (scheme == null) return Destination.BLOCKED;
            scheme = scheme.toLowerCase(Locale.ROOT);
            if (scheme.equals("mailto")) return Destination.EMAIL;
            if (scheme.equals("tel")) return Destination.PHONE;
            if (!scheme.equals("https") && !scheme.equals("http")) return Destination.BLOCKED;
            if (uri.getHost() == null || uri.getUserInfo() != null) return Destination.BLOCKED;
            String path = uri.getPath() == null ? "" : uri.getPath().toLowerCase(Locale.ROOT);
            boolean document = path.endsWith(".pdf") || path.endsWith(".epub") || path.endsWith(".zip");
            if (scheme.equals("https") && "notes.thatvetguy.net".equalsIgnoreCase(uri.getHost())
                    && (uri.getPort() == -1 || uri.getPort() == 443) && !document) return Destination.INTERNAL;
            return Destination.BROWSER;
        } catch (Exception ignored) {
            return Destination.BLOCKED;
        }
    }
}
