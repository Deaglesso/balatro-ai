import os
import signal
import subprocess
import time
import requests


class BalatroServer:

    def __init__(self, port: int):
        self.port = port
        self.url = f"http://127.0.0.1:{port}"
        self.proc = None
        print(self.url)

    def start(self):

        cmd = [
            "uvx",
            "balatrobot",
            "serve",
            "--port", str(self.port),
            "--headless",
            "--fast",
            "--no-shaders",
            "--fps-cap", "1000",
            "--gamespeed", "4",
        ]

        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        self._wait_until_ready()

    def _wait_until_ready(self, timeout=30):

        start = time.time()

        while time.time() - start < timeout:
            try:
                requests.post(self.url, json={
                    "jsonrpc": "2.0",
                    "method": "menu",
                    "params": {},
                    "id": 1,
                })
                return
            except:
                time.sleep(0.25)

        raise RuntimeError("BalatroBot failed to start")

    def stop(self):

        if self.proc:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass

            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
                self.proc.wait()