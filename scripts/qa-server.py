#!/usr/bin/env python3
"""Serve the static export with the compression and cache policy used by Pages."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit,unquote
import sys,mimetypes,gzip
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        redirect_file=ROOT/'_redirects'
        if redirect_file.exists():
            for line in redirect_file.read_text().splitlines():
                parts=line.split()
                if len(parts)==3 and parts[0]==urlsplit(self.path).path and parts[2] in ['301','302','303','307','308']:
                    self.send_response(int(parts[2]));self.send_header('Location',parts[1]);self.send_header('Content-Length','0');self.end_headers();return
        path=(ROOT/unquote(urlsplit(self.path).path).lstrip('/')).resolve()
        if not path.is_relative_to(ROOT):self.send_error(403);return
        if path.is_dir():path=path/'index.html'
        if not path.is_file():self.send_error(404);return
        data=path.read_bytes();mime=mimetypes.guess_type(str(path))[0] or 'application/octet-stream';compressed=False
        if 'gzip' in self.headers.get('Accept-Encoding','') and path.suffix in ['.html','.css','.js','.json','.txt','.xml','.md','.svg']:
            data=gzip.compress(data);compressed=True
        self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Vary','Accept-Encoding')
        self.send_header('Cache-Control','public, max-age=31536000, immutable' if '/assets/' in self.path else 'public, max-age=0, must-revalidate')
        if compressed:self.send_header('Content-Encoding','gzip')
        self.end_headers();self.wfile.write(data)
    def log_message(self,*args):pass
ThreadingHTTPServer(('127.0.0.1',4173),Handler).serve_forever()
