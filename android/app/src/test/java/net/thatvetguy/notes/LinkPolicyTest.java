package net.thatvetguy.notes;
import org.junit.Test;
import static org.junit.Assert.assertEquals;
import static net.thatvetguy.notes.LinkPolicy.Destination.*;
public class LinkPolicyTest {
    @Test public void notesStayInside() {
        assertEquals(INTERNAL, LinkPolicy.classify(LinkPolicy.HOME));
        assertEquals(INTERNAL, LinkPolicy.classify("https://notes.thatvetguy.net/books/?q=MiniVet#clinical"));
    }
    @Test public void documentsAndOtherSitesUsePhoneApps() {
        assertEquals(BROWSER, LinkPolicy.classify("https://notes.thatvetguy.net/assets/outline.PDF"));
        assertEquals(BROWSER, LinkPolicy.classify("https://drive.google.com/file/d/example/view"));
        assertEquals(BROWSER, LinkPolicy.classify("https://download.vet-ebooks.com/example"));
        assertEquals(EMAIL, LinkPolicy.classify("mailto:contact@thatvetguy.net?subject=Report&body=Issue%3A%20broken%20link"));
        assertEquals(PHONE, LinkPolicy.classify("tel:+910000000000"));
    }
    @Test public void lookalikesAndUnsafeSchemesCannotBecomeTrustedPages() {
        assertEquals(BROWSER, LinkPolicy.classify("https://notes.thatvetguy.net.evil.example/"));
        assertEquals(BROWSER, LinkPolicy.classify("http://notes.thatvetguy.net/"));
        assertEquals(BROWSER, LinkPolicy.classify("https://notes.thatvetguy.net:8443/"));
        assertEquals(BLOCKED, LinkPolicy.classify("https://notes.thatvetguy.net@evil.example/"));
        for (String value : new String[]{"javascript:alert(1)","file:///etc/passwd","content://private","intent://example","https:///broken",null}) assertEquals(BLOCKED, LinkPolicy.classify(value));
    }
}
