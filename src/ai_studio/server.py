import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from ai_studio.runtime import Runtime, USERS


def make_handler(runtime):
    class Handler(BaseHTTPRequestHandler):
        def json(self, code, payload):
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.dispatch("GET")

        def do_POST(self):
            self.dispatch("POST")

        def dispatch(self, method):
            try:
                self.route(method)
            except PermissionError as error:
                self.json(403, {"error": str(error)})
            except LookupError as error:
                self.json(404, {"error": str(error)})
            except (ValueError, TypeError):
                self.json(400, {"error": "请求无效，请检查模型、任务状态、输入长度或本地额度"})
            except (BrokenPipeError, ConnectionResetError):
                pass

        def route(self, method):
            path = urlsplit(self.path).path
            if method == "GET" and path == "/":
                page = Path(__file__).with_name("index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
                return
            header = self.headers.get("Authorization", "")
            user = USERS.get(header[7:]) if header.startswith("Bearer ") else None
            if user is None:
                self.json(401, {"error": "缺少有效的本地访问密钥"})
                return
            if method == "GET" and path == "/api/profile":
                self.json(200, runtime.profile(user))
            elif method == "GET" and path == "/api/catalog":
                self.json(200, {"models": runtime.models(user), "tools": [{"name": tool.name, "description": tool.description} for tool in runtime.tools.list_tools()]})
            elif method == "GET" and path == "/api/runs":
                self.json(200, {"runs": runtime.list_runs(user)})
            elif method == "POST" and path == "/api/runs":
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 16384:
                    self.json(413, {"error": "请求体应小于 16 KB"})
                    return
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError("请求必须是对象")
                if not isinstance(data.get("target"), str) or not isinstance(data.get("kind"), str):
                    raise ValueError("缺少任务类型或目标")
                self.json(202, runtime.create(user, data["kind"], data["target"], data.get("prompt")))
            elif path.startswith("/api/runs/"):
                parts = path.strip("/").split("/")
                if method == "GET" and len(parts) == 3:
                    self.json(200, runtime.get(user, parts[2]))
                elif method == "POST" and len(parts) == 4 and parts[3] == "cancel":
                    self.json(200, runtime.cancel(user, parts[2]))
                else:
                    self.json(404, {"error": "接口不存在"})
            elif method == "GET" and path.startswith("/api/assets/"):
                content = runtime.asset(user, path.rsplit("/", 1)[-1])
                self.send_response(200)
                self.send_header("Content-Type", "image/svg+xml")
                self.send_header("Content-Security-Policy", "default-src 'none'; sandbox")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.json(404, {"error": "接口不存在"})
    return Handler


def main():
    runtime = Runtime()
    address = ("127.0.0.1", int(os.environ.get("STUDIO_PORT", "8081")))
    server = ThreadingHTTPServer(address, make_handler(runtime))
    print(f"AI Studio: http://{address[0]}:{address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        runtime.close()
