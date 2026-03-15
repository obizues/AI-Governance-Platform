import subprocess
import sys
import os
import time
import shutil
import requests


def _configure_local_ollama_defaults():
    os.environ.setdefault("AI_EXTRACTION_MODE", "llm")
    os.environ.setdefault("LLM_PROVIDER", "ollama")
    os.environ.setdefault("LLM_MODEL", "llama3.2")
    os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")


def _check_ollama_health(base_url: str) -> bool:
    health_url = base_url.replace("/v1", "").rstrip("/") + "/api/tags"
    try:
        response = requests.get(health_url, timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _start_ollama_server() -> bool:
    ollama_exe = shutil.which("ollama")
    if not ollama_exe:
        print("[launcher] 'ollama' executable not found in PATH.")
        return False

    try:
        subprocess.Popen(
            [ollama_exe, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[launcher] Started 'ollama serve' in background.")
        return True
    except Exception as ex:
        print(f"[launcher] Failed to start Ollama automatically: {ex}")
        return False


def _ensure_ollama_running(base_url: str, wait_seconds: int = 15) -> bool:
    if _check_ollama_health(base_url):
        return True

    started = _start_ollama_server()
    if not started:
        return False

    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if _check_ollama_health(base_url):
            return True
        time.sleep(1)

    return False

if __name__ == "__main__":
    _configure_local_ollama_defaults()
    ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_ok = _ensure_ollama_running(ollama_base)
    if ollama_ok:
        print("[launcher] Local Ollama ready - LLM extraction enabled.")
    else:
        print("[launcher] Ollama not reachable after auto-start attempt; extraction will safely fall back if needed.")

    subprocess.run([
        sys.executable,
        "-m", "streamlit", "run",
        os.path.join("ai_governance_platform", "ui", "app.py")
    ])