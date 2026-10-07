"""
run.py

This script is the final step in the data pipeline for the ClubArc project. 
It runs the load, transform, and validate scripts in sequence and then launches the Streamlit web application.

The extraction step is kept separate because it requires an API key,
while the rest of the pipeline can be reproduced from the raw data included in the repository.
"""

import subprocess
import sys
import os

# Use the same DuckDB database across each stage of the pipeline.
env = os.environ.copy()
env["CLUBARC_DB_PATH"] = "database/clubarc.duckdb"

# Run the load, transform and validate scripts in sequence.
subprocess.run([sys.executable, "src/load.py"], check=True, env=env)
subprocess.run([sys.executable, "src/transform.py"], check=True, env=env)
subprocess.run([sys.executable, "src/validate.py"], check=True, env=env)

# Launch the Streamlit web application.
subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app/app.py"
], env=env)