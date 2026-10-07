"""
Transform.py

This script is the third step in the data pipeline for the ClubArc project.
It transforms the loaded match data into summary and progress views for each Premier League club
in the DuckDB database.
"""

from pathlib import Path
import duckdb
import os

DB_PATH = Path(os.getenv("CLUBARC_DB_PATH", "database/clubarc.duckdb"))

SQL_FILES = [
    Path("sql/01_team_match_results.sql"), # This SQL file creates a view that summarizes match results for each team.
    Path("sql/02_team_season_summary.sql"), # This SQL file creates a view that aggregates match results into a season summary for each team.
    Path("sql/03_team_season_progress.sql") # Tracks each team's cumulative performance throughout a season.
] # List of SQL files to execute

con = duckdb.connect(database=DB_PATH, read_only=False)

for sql_file in SQL_FILES:
    sql = sql_file.read_text()
    con.execute(sql)
    print(f"Applied {sql_file.name}")

con.close()