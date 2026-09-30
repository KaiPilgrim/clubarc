CREATE OR REPLACE VIEW season_summary_validation AS

SELECT
    summary.season_start_year,
    summary.team_id,
    summary.team_name,

    summary.played = reference.played AS played_match,
    summary.wins = reference.wins AS wins_match,
    summary.draws = reference.draws AS draws_match,
    summary.losses = reference.losses AS losses_match,

    summary.goals_for = reference.goals_for AS goals_for_match,
    summary.goals_against = reference.goals_against AS goals_against_match,
    summary.goal_difference = reference.goal_difference AS goal_difference_match,

    summary.points = reference.points AS points_match,
    summary.league_position = reference.position AS position_match,

    (
        summary.played = reference.played
        AND summary.wins = reference.wins
        AND summary.draws = reference.draws
        AND summary.losses = reference.losses
        AND summary.goals_for = reference.goals_for
        AND summary.goals_against = reference.goals_against
        AND summary.goal_difference = reference.goal_difference
        AND summary.points = reference.points
        AND summary.league_position = reference.position
    ) AS valid

FROM team_season_summary AS summary

JOIN standings_reference AS reference
    ON summary.season_start_year = reference.season_start_year
    AND summary.team_id = reference.team_id;