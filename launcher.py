import subprocess
import sys
import os

if __name__ == "__main__":
    subprocess.run([
        sys.executable,
        "-m", "streamlit", "run",
        os.path.join("ai_governance_platform", "ui", "app.py")
    ])
