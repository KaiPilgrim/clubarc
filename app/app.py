"""
app.py

This script is the Streamlit web application for the ClubArc project.
The app lets users explore a Premier League club's performance across
multiple seasons, view cumulative points trajectories, and compare
seasons after the same number of completed matches.

The application reads from the transformed DuckDB views created by
the ClubArc data pipeline.
"""

from pathlib import Path
import duckdb
import streamlit as st
import subprocess
import sys
import os


st.set_page_config(
    page_title="ClubArc",
    layout="wide"
)


# Use the local pipeline database when provided; otherwise build a temporary database for deployment.
local_db_path = os.getenv("CLUBARC_DB_PATH")


if local_db_path:
    DB_PATH = Path(local_db_path)

else:
    DB_PATH = Path("/tmp/clubarc.duckdb")
    
    if not DB_PATH.exists():
        BUILD_PATH = Path(f"/tmp/clubarc_build_{os.getpid()}.duckdb")
        env = os.environ.copy()
        env["CLUBARC_DB_PATH"] = str(BUILD_PATH)

        subprocess.run([sys.executable, "src/load.py"], check=True, env=env)
        subprocess.run([sys.executable, "src/transform.py"], check=True, env=env)

        os.replace(BUILD_PATH, DB_PATH)

con = duckdb.connect(database=DB_PATH, read_only=True)

# Load the available clubs from the season summary view.
teams = con.execute("""
    SELECT DISTINCT
        team_id,
        team_name
    FROM team_season_summary
    ORDER BY team_name
""").fetchall()

st.title("ClubArc")
st.subheader("Premier League Club Analytics")

team_names = [team[1] for team in teams]

selected_team = st.selectbox(
    "Select a Premier League club",
    team_names
)

selected_team_id = next(
    team[0] for team in teams
    if team[1] == selected_team
)


st.subheader(f"{selected_team} Season Overview")

# Show each season's final performance for the selected club.
summary = con.execute("""
    SELECT
        CAST(season_start_year AS VARCHAR)
            || '/'
            || RIGHT(CAST(season_start_year + 1 AS VARCHAR), 2) AS season,
        league_position AS position,
        played,
        wins,
        draws,
        losses,
        goals_for,
        goals_against,
        goal_difference,
        points,
        points_per_game
    FROM team_season_summary
    WHERE team_id = ?
    ORDER BY season_start_year
""", [selected_team_id]).df()

st.dataframe(
    summary,
    hide_index=True,
    width='stretch'
)

# Compare the selected club's cumulative points trajectory across seasons.
progress = con.execute("""
    SELECT
        season_start_year,
        club_match_number,
        cumulative_points
    FROM team_season_progress
    WHERE team_id = ?
    ORDER BY season_start_year, club_match_number
""", [selected_team_id]).df()

st.subheader("Season Trajectory")

chart_data = progress.pivot(
    index="club_match_number",
    columns="season_start_year",
    values="cumulative_points"
)

st.line_chart(chart_data)

# Limit comparisons to the number of matches completed in the current season.
current_season_matches = con.execute("""
    SELECT MAX(club_match_number)
    FROM team_season_progress
    WHERE team_id = ?
      AND season_start_year = 2026
""", [selected_team_id]).fetchone()[0]

if current_season_matches is not None:
    max_matches = min(current_season_matches, 38)
else:
    max_matches = 38

# Let the user choose the gameweek to compare across seasons.
compare_after = st.slider(
    "Compare seasons after completed matches",
    min_value=1,
    max_value=max_matches,
    value=max_matches
)
# Compare each season at the same point in the campaign.
comparison = con.execute("""
    SELECT
        season_start_year,
        cumulative_wins AS wins,
        cumulative_draws AS draws,
        cumulative_losses AS losses,
        cumulative_goals_for AS goals_for,
        cumulative_goals_against AS goals_against,
        cumulative_goal_difference AS goal_difference,
        cumulative_points AS points,
        cumulative_points_per_game AS points_per_game
    FROM team_season_progress
    WHERE team_id = ?
      AND club_match_number = ?
    ORDER BY season_start_year
""", [selected_team_id, compare_after]).df()

st.subheader(f"Performance after {compare_after} completed matches")

st.dataframe(
    comparison,
    hide_index=True,
    width='stretch'
)

st.caption("Football data provided by the Football-Data.org API")

con.close()