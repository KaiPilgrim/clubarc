import json
from pathlib import Path
import duckdb


RAW_DIR = Path("data/raw")
DB_PATH = Path("database/clubarc.duckdb")
SEASONS = [2023, 2024, 2025, 2026]

con = duckdb.connect(database=DB_PATH, read_only=False)

con.execute("""
    CREATE OR REPLACE TABLE standings_reference (
        season_start_year INTEGER,
        team_id INTEGER,
        position INTEGER,
        played INTEGER,
        wins INTEGER,
        draws INTEGER,
        losses INTEGER,
        goals_for INTEGER,
        goals_against INTEGER,
        goal_difference INTEGER,
        points INTEGER
    )
""")


for season in SEASONS:
    input_file = RAW_DIR / f"pl_standings_{season}.json"

    with open(input_file, "r") as file:
        data = json.load(file)

    total_standings = next(
        standing for standing in data["standings"]
        if standing["type"] == "TOTAL"
    )

    rows = []

    for team in total_standings["table"]:
        rows.append((
            season,
            team["team"]["id"],
            team["position"],
            team["playedGames"],
            team["won"],
            team["draw"],
            team["lost"],
            team["goalsFor"],
            team["goalsAgainst"],
            team["goalDifference"],
            team["points"]
        ))

    con.executemany("""
        INSERT INTO standings_reference
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    print(f"Loaded {season} reference standings")


validation_sql = Path(
    "sql/03_validate_team_season_summary.sql"
).read_text()

con.execute(validation_sql)

mismatches = con.execute("""
    SELECT *
    FROM season_summary_validation
    WHERE valid = FALSE
""").fetchall()

print(f"Validation mismatches: {len(mismatches)}")

con.close()