CREATE OR REPLACE VIEW team_season_summary AS

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

        SUM(points) FILTER (WHERE venue = 'HOME') AS home_points,
        SUM(points) FILTER (WHERE venue = 'AWAY') AS away_points

    FROM team_match_results

    GROUP BY
        season_start_year,
        season_id,
        team_id,
        team_name
),

ranked AS (

    SELECT
        *,
        ROUND(points::DOUBLE / played, 2) AS points_per_game,

        ROW_NUMBER() OVER (
            PARTITION BY season_start_year
            ORDER BY
                points DESC,
                goal_difference DESC,
                goals_for DESC
        ) AS league_position

    FROM season_totals
)

SELECT *
FROM ranked;