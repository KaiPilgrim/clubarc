from pathlib import Path
import duckdb

DB_PATH = Path("database/clubarc.duckdb")
SQL_FILE = Path("sql/01_team_match_results.sql")

con = duckdb.connect(database=DB_PATH, read_only=False)

sql = SQL_FILE.read_text()
con.execute(sql)