/*
03_team_season_progress.sql

Shows each team's cumulative performance after every match across the season.
*/

CREATE OR REPLACE VIEW team_season_progress AS

-- Create a cumulative progress view for each team in each season by aggregating the match results.
WITH progress AS (

    SELECT
        season_start_year,
        season_id,
        team_id,
        team_name,

        club_match_number,
        utc_date,

        opponent_team_id,
        opponent_team_name,
        venue,
        result,

    -- Calculate each team's cumulative totals after every completed match.
        SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END)
            OVER (
                PARTITION BY season_start_year, team_id
                ORDER BY club_match_number
            ) AS cumulative_wins,

        SUM(CASE WHEN result = 'D' THEN 1 ELSE 0 END)
            OVER (
                PARTITION BY season_start_year, team_id
                ORDER BY club_match_number
            ) AS cumulative_draws,

        SUM(CASE WHEN result = 'L' THEN 1 ELSE 0 END)
            OVER (
                PARTITION BY season_start_year, team_id
                ORDER BY club_match_number
            ) AS cumulative_losses,

        SUM(goals_for)
            OVER (
                PARTITION BY season_start_year, team_id
                ORDER BY club_match_number
            ) AS cumulative_goals_for,

        SUM(goals_against)
            OVER (
                PARTITION BY season_start_year, team_id
                ORDER BY club_match_number
            ) AS cumulative_goals_against,

        SUM(points)
            OVER (
                PARTITION BY season_start_year, team_id
                ORDER BY club_match_number
            ) AS cumulative_points

    FROM team_match_results
)

-- Calculate the cumulative goal difference and points per game for each team in each season.
SELECT
    *,
    cumulative_goals_for - cumulative_goals_against
        AS cumulative_goal_difference,

    ROUND(
        cumulative_points::DOUBLE / club_match_number,
        2
    ) AS cumulative_points_per_game

FROM progress;