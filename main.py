"""Dependency-free browser Jarvis server, suitable for Render."""

from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.parse import quote_plus


ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "templates" / "index.html"
LINKS = {
    "google": "https://www.google.com/",
    "youtube": "https://www.youtube.com/",
    "facebook": "https://www.facebook.com/",
    "instagram": "https://www.instagram.com/",
    "linkedin": "https://www.linkedin.com/",
    "whatsapp": "https://web.whatsapp.com/",
    "gmail": "https://mail.google.com/",
    "github": "https://github.com/",
    "maps": "https://maps.google.com/",
}


def process_command(command):
    """Turn a voice or typed command into a safe reply and optional URL."""
    text = " ".join(command.strip().lower().split())
    if not text:
        return {"reply": "Kuch boliye, main sun raha hoon."}

    target = ""
    if text.startswith("open "):
        target = text[5:]
    elif text.endswith(" kholo"):
        target = text[:-6]
    elif text.endswith(" khol do"):
        target = text[:-8]
    elif text.startswith("chalao "):
        target = text[7:]
    target = target.strip(" .!? ")
    for name, url in LINKS.items():
        if target and (name in target or (name == "maps" and "map" in target)):
            return {"reply": f"{name.title()} khol raha hoon.", "url": url}

    if any(word in text for word in ("time", "samay", "kitne baje")):
        return {"reply": "Abhi " + datetime.now().strftime("%I:%M %p") + " baj rahe hain."}
    if any(word in text for word in ("date", "tareekh", "aaj kya din")):
        return {"reply": "Aaj " + datetime.now().strftime("%A, %d %B %Y") + " hai."}
    if any(word in text for word in ("hello", "hi jarvis", "namaste", "salaam")):
        return {"reply": "Namaste! Main aapki kya madad karoon?"}
    if any(word in text for word in ("your name", "tumhara naam", "who are you", "kaun ho")):
        return {"reply": "Main Jarvis hoon, aapka browser assistant."}
    if any(word in text for word in ("search", "dhundo", "dhoondo", "khojo")):
        query = text
        for prefix in ("search for ", "search ", "google ", "dhundo ", "dhoondo ", "khojo "):
            if query.startswith(prefix):
                query = query[len(prefix):]
                break
        if query:
            return {"reply": f"{query} ke liye search khol raha hoon.", "url": "https://www.google.com/search?q=" + quote_plus(query)}
    if any(word in text for word in ("play ", "gaana", "song", "music")):
        query = text
        for prefix in ("play ", "gaana ", "song ", "music "):
            if query.startswith(prefix):
                query = query[len(prefix):]
                break
        return {"reply": "YouTube par music dhoondh raha hoon.", "url": "https://www.youtube.com/results?search_query=" + quote_plus(query or "music")}

    return {"reply": "Yeh command abhi nahi aati. Website kholne, time/date batane, search karne ya YouTube par gaana dhoondhne ko kahiye."}


class JarvisHandler(BaseHTTPRequestHandler):
    def _send(self, status, content_type, body):
        encoded = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            try:
                self._send(200, "text/html; charset=utf-8", PAGE.read_text(encoding="utf-8"))
            except OSError:
                self._send(500, "text/plain; charset=utf-8", "Jarvis page is missing")
        elif self.path == "/health":
            self._send(200, "application/json; charset=utf-8", json.dumps({"status": "ok"}))
        else:
            self._send(404, "text/plain; charset=utf-8", "Not found")

    def do_POST(self):
        if self.path != "/api/command":
            self._send(404, "application/json; charset=utf-8", json.dumps({"reply": "Not found"}))
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > 4096:
                raise ValueError("Request too large")
            data = json.loads(self.rfile.read(length) or b"{}")
            text = data.get("command", "") if isinstance(data, dict) else ""
            if not isinstance(text, str) or len(text) > 300:
                self._send(400, "application/json; charset=utf-8", json.dumps({"reply": "Command 300 characters se chhoti honi chahiye."}))
                return
            result = process_command(text)
            self._send(200, "application/json; charset=utf-8", json.dumps(result, ensure_ascii=False))
        except (ValueError, json.JSONDecodeError):
            self._send(400, "application/json; charset=utf-8", json.dumps({"reply": "Invalid request"}))

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), JarvisHandler)
    print(f"Jarvis is listening on port {port}")
    server.serve_forever()
