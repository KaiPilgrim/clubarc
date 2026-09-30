# Importation necessary libraries
import os # To access environment variables
import requests  #  To make HTTP requests
from pathlib import Path # To handle file paths
from dotenv import load_dotenv # To load environment variables from a .env file


load_dotenv() # Load environment variables from a .env file

# Retrieve the API key from environment variables
api_key = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
SEASONS = [2023, 2024, 2025, 2026]
headers = {"X-Auth-Token": api_key}
RAW_DIR = Path("data/raw")

def extract_matches(season):
    url = f"{BASE_URL}/competitions/PL/matches"

    response = requests.get(url, headers=headers, params={"season": season}, timeout=30)

    response.raise_for_status()

    output_file = RAW_DIR / f"pl_matches_{season}.json"
    output_file.write_bytes(response.content)

    print(f"Saved {season} matches")


def extract_standings(season):
    url = f"{BASE_URL}/competitions/PL/standings"

    response = requests.get(url, headers=headers, params={"season": season}, timeout=30)

    response.raise_for_status()

    output_file = RAW_DIR / f"pl_standings_{season}.json"
    output_file.write_bytes(response.content)

    print(f"Saved {season} standings")

for season in SEASONS:
    extract_matches(season)
    extract_standings(season)

