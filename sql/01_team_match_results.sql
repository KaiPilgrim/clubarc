/*
01_team_match_results.sql

Creates a match results view from the raw matches table.
For each finished match two rows are created: one for the home team and one for the away team.
Shows each team's completed matches in chronological order for every season it participates in.


*/

CREATE OR REPLACE VIEW team_match_results AS 

-- Create one row per team per match by combining the home and away perspectives.
WITH team_rows AS (

    SELECT
        match_id,
        season_start_year,
        season_id,
        utc_date,
        matchday,

        home_team_id AS team_id,
        home_team_name AS team_name,
        away_team_id AS opponent_team_id,
        away_team_name AS opponent_team_name,

        'HOME' AS venue,

        home_goals AS goals_for,
        away_goals AS goals_against,

        -- Determine the result and points for the home team from the goals scored and conceded.
        CASE
            WHEN home_goals > away_goals THEN 'W'
            WHEN home_goals = away_goals THEN 'D'
            ELSE 'L'
        END AS result,

        CASE
            WHEN home_goals > away_goals THEN 3
            WHEN home_goals = away_goals THEN 1
            ELSE 0
        END AS points

    -- Only completed matches are included so results and points are final.
    FROM matches
    WHERE status = 'FINISHED'

    -- Number each team's completed matches chronologically within each season.
    UNION ALL

    SELECT
        match_id,
        season_start_year,
        season_id,
        utc_date,
        matchday,

        away_team_id AS team_id,
        away_team_name AS team_name,
        home_team_id AS opponent_team_id,
        home_team_name AS opponent_team_name,

        'AWAY' AS venue,

        away_goals AS goals_for,
        home_goals AS goals_against,

        -- Determine the result and points for the away team from the goals scored and conceded.
        CASE
            WHEN away_goals > home_goals THEN 'W'
            WHEN away_goals = home_goals THEN 'D'
            ELSE 'L'
        END AS result,

        CASE
            WHEN away_goals > home_goals THEN 3
            WHEN away_goals = home_goals THEN 1
            ELSE 0
        END AS points

-- Only completed matches are included so results and points are final.
    FROM matches
    WHERE status = 'FINISHED'
)

-- Add a club match number to each row so you can see a team's full season from matchday 1 to 38.
SELECT
    *,
    ROW_NUMBER() OVER (
        PARTITION BY season_start_year, team_id
        ORDER BY utc_date, match_id
    ) AS club_match_number
    
FROM team_rows;