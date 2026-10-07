"""
Load.py

This script is the second step in the data pipeline for the ClubArc project.
It is responsible for loading the extracted JSON data into a DuckDB database.
It creates the necessary table and inserts the match data for each season.
"""
import json
from pathlib import Path
import duckdb 
import os


RAW_DIR = Path("data/raw") # Directory where the raw JSON data is stored
DB_PATH = Path(os.getenv("CLUBARC_DB_PATH", "database/clubarc.duckdb")) # Path to the DuckDB database file, retrieved from environment variables or defaulting to 'database/clubarc.duckdb'
SEASONS = [2023, 2024, 2025, 2026]

DB_PATH.parent.mkdir(parents=True, exist_ok=True) # Create the parent directory for the database file if it doesn't exist

con = duckdb.connect(database=DB_PATH, read_only=False) # Connect to the DuckDB database in read-write mode

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
""") # Create or replace the 'matches' table in the database with the specified columns and data types


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
        )) # Select fields required for the matches table
        
    con.executemany("""
        INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows) # Insert all the rows for the current season into the 'matches' table in the database using a single SQL statement

    print(f"Loaded {season}: {len(rows)} matches")


total_matches = con.execute(
    "SELECT COUNT(*) FROM matches"
).fetchone()[0]

print(f"Total matches loaded: {total_matches}")

con.close()