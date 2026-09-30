CREATE OR REPLACE VIEW team_match_results AS

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

    FROM matches
    WHERE status = 'FINISHED'

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

    FROM matches
    WHERE status = 'FINISHED'
)

SELECT
    *,
    ROW_NUMBER() OVER (
        PARTITION BY season_start_year, team_id
        ORDER BY utc_date, match_id
    ) AS club_match_number

FROM team_rows;