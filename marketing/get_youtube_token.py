#!/usr/bin/env python3
"""一次性取得 YouTube 上傳用的 refresh token。

前置:Google Cloud Console 啟用 YouTube Data API v3、建立 OAuth 用戶端
(類型「桌面應用程式」),拿到 client_id / client_secret。

用法:
    python get_youtube_token.py <client_id> <client_secret>

跑完會印出 YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN 三行,
貼進 marketing/.env 即可。refresh token 不會過期(除非撤銷授權)。
"""
import http.server
import json
import sys
import urllib.parse
import urllib.request
import webbrowser

PORT = 8723
REDIRECT = f"http://localhost:{PORT}/"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"


def main():
    if len(sys.argv) < 3:
        sys.exit("用法:python get_youtube_token.py <client_id> <client_secret>")
    cid, csecret = sys.argv[1], sys.argv[2]

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": REDIRECT, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent",
    })

    box = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            box["code"] = q.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("授權完成,可以關掉這個分頁回終端機。".encode())

        def log_message(self, *a):
            pass

    print(f"開啟瀏覽器授權中...\n沒自動開就手動貼:\n{auth_url}\n")
    webbrowser.open(auth_url)
    srv = http.server.HTTPServer(("localhost", PORT), Handler)
    while "code" not in box:
        srv.handle_request()
    if not box.get("code"):
        sys.exit("沒拿到授權碼")

    data = urllib.parse.urlencode({
        "code": box["code"], "client_id": cid, "client_secret": csecret,
        "redirect_uri": REDIRECT, "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token",
                                 data=data, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        tok = json.loads(r.read().decode())

    rt = tok.get("refresh_token")
    if not rt:
        sys.exit(f"沒拿到 refresh token(可能未加 prompt=consent):{tok}")
    print("\n✅ 取得成功 —— 把這三行填進 marketing/.env:\n")
    print(f"YT_CLIENT_ID={cid}")
    print(f"YT_CLIENT_SECRET={csecret}")
    print(f"YT_REFRESH_TOKEN={rt}")


if __name__ == "__main__":
    main()
