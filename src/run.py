import subprocess
import sys


subprocess.run([sys.executable, "src/load.py"], check=True)
subprocess.run([sys.executable, "src/transform.py"], check=True)
subprocess.run([sys.executable, "src/validate.py"], check=True)

subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app/app.py"
])