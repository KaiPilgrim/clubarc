from pathlib import Path
import duckdb
import os

DB_PATH = Path(os.getenv("CLUBARC_DB_PATH", "database/clubarc.duckdb"))

SQL_FILES = [
    Path("sql/01_team_match_results.sql"),
    Path("sql/02_team_season_summary.sql"),
    Path("sql/04_team_season_progress.sql")
]

con = duckdb.connect(database=DB_PATH, read_only=False)

for sql_file in SQL_FILES:
    sql = sql_file.read_text()
    con.execute(sql)
    print(f"Applied {sql_file.name}")

con.close()