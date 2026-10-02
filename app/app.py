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

local_db_path = os.getenv("CLUBARC_DB_PATH")


if local_db_path:
    DB_PATH = Path(local_db_path)

else:
    DB_PATH = Path(
        f"/tmp/clubarc_{os.getpid()}.duckdb"
    )
    
    if not DB_PATH.exists():
        env = os.environ.copy()
        env["CLUBARC_DB_PATH"] = str(DB_PATH)

        subprocess.run([sys.executable, "src/load.py"], check=True, env=env)
        subprocess.run([sys.executable, "src/transform.py"], check=True, env=env)

con = duckdb.connect(database=DB_PATH, read_only=True)

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

compare_after = st.slider(
    "Compare seasons after completed matches",
    min_value=1,
    max_value=max_matches,
    value=max_matches
)

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

con.close()