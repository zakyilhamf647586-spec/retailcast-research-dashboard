"""Launch a real Streamlit server and verify its HTTP health endpoint.

Run after installing requirements and running the AppTest suite.
"""
import contextlib
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    with contextlib.closing(socket.socket()) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    cmd = [sys.executable,"-m","streamlit","run","app.py",
           "--server.headless=true", "--browser.gatherUsageStats=false",
           "--server.address=127.0.0.1", f"--server.port={port}"]
    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    try:
        end = time.monotonic() + 45
        while time.monotonic() < end:
            if proc.poll() is not None:
                output=proc.stdout.read()
                raise RuntimeError(f"Streamlit exited early ({proc.returncode}):\n{output[-3000:]}")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/_stcore/health",timeout=2) as res:
                    if res.status == 200 and res.read().strip() == b"ok":
                        print(f"PASS: real Streamlit HTTP server is healthy at localhost:{port}")
                        return
            except (OSError, TimeoutError):
                time.sleep(0.5)
        raise TimeoutError("Streamlit did not pass health check in 45 seconds")
    finally:
        proc.terminate()
        try: proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill();proc.communicate()

if __name__ == "__main__":
    main()
