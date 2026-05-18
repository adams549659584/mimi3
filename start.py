#!/usr/bin/env python3
"""
自动检测 ngrok 隧道并启动 mimo2api 网关。

Usage:
  python start.py
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"
POLL_INTERVAL = 1
POLL_TIMEOUT = 30


def query_ngrok_api() -> str | None:
    """查询 ngrok 本地 API，返回公网 WebSocket URL，失败返回 None。"""
    try:
        with urllib.request.urlopen(NGROK_API_URL, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            for t in data.get("tunnels", []):
                public_url = t.get("public_url", "")
                if public_url.startswith("https://"):
                    return public_url.replace("https://", "wss://") + "/ws"
                elif public_url.startswith("http://"):
                    return public_url.replace("http://", "ws://") + "/ws"
    except (urllib.error.URLError, OSError, json.JSONDecodeError, KeyError):
        pass
    return None


def wait_for_ngrok() -> str:
    """轮询 ngrok API 直到获取到隧道 URL，超时则抛出异常。"""
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        url = query_ngrok_api()
        if url:
            return url
        time.sleep(POLL_INTERVAL)
    raise RuntimeError(
        f"等待 ngrok 隧道超时（{POLL_TIMEOUT}s），地址: {NGROK_API_URL}\n"
        "请确认 ngrok 已启动: http://127.0.0.1:4040"
    )


def start_ngrok():
    """启动 ngrok 子进程。如果已在运行则复用。"""
    if query_ngrok_api():
        print("[start.py] 检测到已有 ngrok 隧道，复用现有连接。")
        return

    print("[start.py] 正在启动 ngrok 隧道...")
    kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    port = os.getenv("SERVER_PORT", "8000")
    cmd = ["ngrok", "http", port]
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    if authtoken:
        cmd.extend(["--authtoken", authtoken])
    subprocess.Popen(cmd, **kwargs)


def main():
    start_ngrok()
    ws_url = wait_for_ngrok()

    print(f"[start.py] 检测到 ngrok 隧道地址: {ws_url}")
    os.environ["WS_TUNNEL_URL"] = ws_url

    import main as app_main
    app_main.main()


if __name__ == "__main__":
    main()
