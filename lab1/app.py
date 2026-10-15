from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from converter import convert_all


class ColorHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        with open("index.html", "rb") as f:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f.read())

    def do_POST(self):
        if self.path == "/convert":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            result = convert_all(
                data["source"], data["values"], data.get("prev_h", 0.0)
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))


if __name__ == "__main__":
    print("http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), ColorHandler).serve_forever()