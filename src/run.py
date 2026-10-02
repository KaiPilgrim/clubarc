import subprocess
import sys
import os


env = os.environ.copy()
env["CLUBARC_DB_PATH"] = "database/clubarc.duckdb"

subprocess.run([sys.executable, "src/load.py"], check=True, env=env)
subprocess.run([sys.executable, "src/transform.py"], check=True, env=env)
subprocess.run([sys.executable, "src/validate.py"], check=True, env=env)

subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app/app.py"
], env=env)