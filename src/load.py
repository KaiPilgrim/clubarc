# Import necessary libraries
import json
from pathlib import Path
import duckdb


RAW_DIR = Path("data/raw")
DB_PATH = Path("database/clubarc.duckdb")
SEASONS = [2023, 2024, 2025, 2026]

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(database=DB_PATH, read_only=False)

con.execute("""
    CREATE OR REPLACE TABLE matches (
        match_id INTEGER PRIMARY KEY,
        season_start_year INTEGER NOT NULL,
        season_id INTEGER NOT NULL,
        utc_date TIMESTAMPTZ NOT NULL,
        status VARCHAR NOT NULL,
        matchday INTEGER NOT NULL,
        home_team_id INTEGER NOT NULL,
        home_team_name VARCHAR NOT NULL,
        away_team_id INTEGER NOT NULL,
        away_team_name VARCHAR NOT NULL,
        home_goals INTEGER,
        away_goals INTEGER
    )
""")


for season in SEASONS:
    input_file = RAW_DIR / f"pl_matches_{season}.json"

    with open(input_file, "r") as file:
        data = json.load(file)

    rows = []

    for match in data["matches"]:
        rows.append((
            match["id"],
            season,
            match["season"]["id"],
            match["utcDate"],
            match["status"],
            match["matchday"],
            match["homeTeam"]["id"],
            match["homeTeam"]["shortName"],
            match["awayTeam"]["id"],
            match["awayTeam"]["shortName"],
            match["score"]["fullTime"]["home"],
            match["score"]["fullTime"]["away"]
        ))

    con.executemany("""
        INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    print(f"Loaded {season}: {len(rows)} matches")


total_matches = con.execute(
    "SELECT COUNT(*) FROM matches"
).fetchone()[0]

print(f"Total matches loaded: {total_matches}")

con.close()