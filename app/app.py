from pathlib import Path

import duckdb
import streamlit as st


DB_PATH = Path("database/clubarc.duckdb")

con = duckdb.connect(database=DB_PATH, read_only=True)

teams = con.execute("""
    SELECT DISTINCT
        team_id,
        team_name
    FROM team_season_summary
    ORDER BY team_name
""").fetchall()

st.set_page_config(
    page_title="ClubArc",
    layout="wide"
)

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
    use_container_width=True
)


