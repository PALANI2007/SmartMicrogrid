"""
Simple HTTP proxy that forwards npm registry requests via Python's urllib.
Runs on http://localhost:4873 and forwards to https://registry.npmjs.org
"""
import http.server
import urllib.request
import urllib.error
import ssl
import sys

TARGET = "https://registry.npmjs.org"
PORT = 4873

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[proxy] {self.path[:60]}: {args[1] if len(args)>1 else ''}")

    def do_GET(self):
        self._proxy("GET")

    def do_HEAD(self):
        self._proxy("HEAD")

    def _proxy(self, method):
        url = TARGET + self.path
        try:
            req = urllib.request.Request(url, method=method)
            req.add_header("Accept", self.headers.get("Accept", "*/*"))
            req.add_header("User-Agent", "python-proxy/1.0")
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(k, v)
                self.end_headers()
                if method == "GET":
                    self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            if method == "GET":
                self.wfile.write(e.read())
        except Exception as e:
            print(f"Error proxying {url}: {e}")
            self.send_response(502)
            self.end_headers()

    def log_request(self, code='-', size='-'):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print(f"npm proxy running on http://localhost:{PORT}")
    server.serve_forever()
