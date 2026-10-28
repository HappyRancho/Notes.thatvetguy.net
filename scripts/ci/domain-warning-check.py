#!/usr/bin/env python3
"""Collect public redirect, certificate and ownership evidence for a Chrome warning."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import socket
import ssl
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/qa/domain-warning'
NOTES = 'https://notes.thatvetguy.net/'
MAIN = 'https://thatvetguy.net/'
URLS = [NOTES, 'http://notes.thatvetguy.net/', MAIN, 'https://www.thatvetguy.net/',
        NOTES + '.well-known/assetlinks.json', MAIN + '.well-known/assetlinks.json']


class Document(HTMLParser):
    def __init__(self, base):
        super().__init__(); self.base = base; self.canonical = []; self.notes_links = []; self.refresh = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical.append(attrs.get('href'))
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh': self.refresh.append(attrs.get('content'))
        if tag == 'a' and attrs.get('href'):
            href = urljoin(self.base, attrs['href']); host = urlsplit(href).hostname or ''
            if 'notes' in host.lower(): self.notes_links.append(href)


class Redirects(HTTPRedirectHandler):
    def __init__(self): self.history = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if len(self.history) >= 6: raise ValueError('Redirect chain exceeded audit limit')
        self.history.append({'status': code, 'from': req.full_url, 'to': urljoin(req.full_url, newurl)})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url):
    history = Redirects(); row = {'url': url}
    try:
        request = Request(url, headers={'User-Agent': 'NotesThatVetGuy-DomainAudit/1', 'Cache-Control': 'no-cache'})
        try: response = build_opener(history).open(request, timeout=15)
        except HTTPError as error: response = error
        with response:
            raw = response.read(1_000_000).decode('utf-8', 'replace')
            row.update(status=response.status, finalURL=response.url,
                       contentType=response.headers.get('Content-Type'),
                       redirects=history.history, httpsResponse=urlsplit(response.url).scheme == 'https')
        document = Document(row['finalURL']); document.feed(raw)
        row.update(canonical=document.canonical, notesLinks=sorted(set(document.notes_links)), metaRefresh=document.refresh)
        title = re.search(r'<title[^>]*>(.*?)</title>', raw, re.I | re.S)
        row['title'] = title[1].strip() if title else None
        row['unicodeHostname'] = urlsplit(row['finalURL']).hostname
        row['asciiHostname'] = (row['unicodeHostname'] or '').encode('idna').decode()
        if url.endswith('/assetlinks.json') and row['status'] == 200:
            try: row['assetLinks'] = json.loads(raw)
            except json.JSONDecodeError: row['assetLinksError'] = 'The URL returns non-JSON content.'
    except Exception as error:
        row.update(error=type(error).__name__ + ': ' + str(error), redirects=history.history)
    return row


def certificate(host):
    row = {'host': host}
    try:
        row['addresses'] = sorted({r[4][0] for r in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
        with socket.create_connection((host, 443), timeout=12) as connection:
            with ssl.create_default_context().wrap_socket(connection, server_hostname=host) as secure:
                info = secure.getpeercert()
                row.update(validated=True, subjectAltNames=info.get('subjectAltName'), expires=info.get('notAfter'),
                           sha256=hashlib.sha256(secure.getpeercert(binary_form=True)).hexdigest(), protocol=secure.version())
    except Exception as error: row.update(validated=False, error=type(error).__name__ + ': ' + str(error))
    return row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool: pages = list(pool.map(fetch, URLS))
    with ThreadPoolExecutor(max_workers=2) as pool: certificates = list(pool.map(certificate, ['notes.thatvetguy.net', 'thatvetguy.net']))
    report = {'pages': pages, 'certificates': certificates,
              'scope': 'Public transport and certificate evidence only. This does not establish Safe Browsing status or clear a Chrome client-side lookalike warning.'}
    (OUT / 'transport.json').write_text(json.dumps(report, indent=2) + '\n')
    print('DOMAIN_TRANSPORT ' + json.dumps(report))
    primary = pages[0]
    if primary.get('status') != 200 or primary.get('finalURL') != NOTES or not certificates[0]['validated']:
        raise SystemExit('The primary Notes HTTPS entry point requires investigation; see transport.json.')


if __name__ == '__main__': main()
