/*
02_team_season_summary.sql

This view recreates a league table for each team in each season based on the match results view.

*/

CREATE OR REPLACE VIEW team_season_summary AS

-- Create a summary of each team's season by aggregating the match results.
WITH season_totals AS (

    SELECT
        season_start_year,
        season_id,
        team_id,
        team_name,

        COUNT(*) AS played,

        COUNT(*) FILTER (WHERE result = 'W') AS wins,
        COUNT(*) FILTER (WHERE result = 'D') AS draws,
        COUNT(*) FILTER (WHERE result = 'L') AS losses,

        SUM(goals_for) AS goals_for,
        SUM(goals_against) AS goals_against,
        SUM(goals_for) - SUM(goals_against) AS goal_difference,

        SUM(points) AS points,

        -- Keep home and away points separate so performance by venue can be compared.
        SUM(points) FILTER (WHERE venue = 'HOME') AS home_points,
        SUM(points) FILTER (WHERE venue = 'AWAY') AS away_points

    -- Use the team_match_results view to aggregate the data for each team in each season.
    FROM team_match_results 
    GROUP BY 
        season_start_year,
        season_id,
        team_id,
        team_name
),

-- Rank the teams in each season based on points, goal difference, and goals scored to determine their league position.
ranked AS ( 

    SELECT
        *,
        -- Calculate the average points per game for each team in each season.
        ROUND(points::DOUBLE / played, 2) AS points_per_game, 

        -- Apply tie breaking rules using the Premier League ranking system when teams are level on points.
        ROW_NUMBER() OVER ( 
            PARTITION BY season_start_year
            ORDER BY
                points DESC,
                goal_difference DESC,
                goals_for DESC
        ) AS league_position

    FROM season_totals 
)

-- Return the final league table for each team in each season.
SELECT *
FROM ranked; 