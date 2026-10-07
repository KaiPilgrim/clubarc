"""
Extract.py

This script is the initial step in the data pipeline for the ClubArc project.
It is responsible for extracting match and standings data for the Premier League from the Football-Data.org API.
The extracted data is saved as JSON files in the 'data/raw' directory for further processing.
"""

import os # To access environment variables
import requests  #  To make HTTP requests
from pathlib import Path # To handle file paths
from dotenv import load_dotenv # To load environment variables from a .env file


load_dotenv() # Load environment variables from a .env file

api_key = os.getenv("FOOTBALL_DATA_API_KEY") # Retrieve the API key from environment variables
BASE_URL = "https://api.football-data.org/v4" # Base URL for the Football-Data.org API
SEASONS = [2023, 2024, 2025, 2026] # List of seasons for which data will be extracted
headers = {"X-Auth-Token": api_key} # Adds the API key to the request headers for authentication
RAW_DIR = Path("data/raw") # Directory where the raw JSON data will be saved
RAW_DIR.mkdir(parents=True, exist_ok=True) # Create the directory if it doesn't exist

def extract_matches(season): # Function to extract match data for a given season
    url = f"{BASE_URL}/competitions/PL/matches"

    response = requests.get(url, headers=headers, params={"season": season}, timeout=30) 

    response.raise_for_status()

    output_file = RAW_DIR / f"pl_matches_{season}.json"
    output_file.write_bytes(response.content) # Save the response content (JSON data) to a file in the 'data/raw' directory

    print(f"Saved {season} matches")


def extract_standings(season): # Function to extract standings data for a given season
    url = f"{BASE_URL}/competitions/PL/standings"

    response = requests.get(url, headers=headers, params={"season": season}, timeout=30) 

    response.raise_for_status()

    output_file = RAW_DIR / f"pl_standings_{season}.json"
    output_file.write_bytes(response.content)

    print(f"Saved {season} standings")

for season in SEASONS: # Loop through each season in the SEASONS list and call the extraction functions
    extract_matches(season)
    extract_standings(season)

