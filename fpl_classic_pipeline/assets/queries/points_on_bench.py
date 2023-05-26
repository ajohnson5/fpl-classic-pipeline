points_on_bench = """
WITH
  base_cte AS (
  SELECT
    manager_id,
    position,
    total_points,
    actual_points,
    (CASE
        WHEN multiplier = 0 THEN total_points
      ELSE
      actual_points
    END
      ) AS total_points_with_captain,
    MAX(multiplier) OVER (PARTITION BY manager_id) AS captaincy_multiplier
  FROM
    $
  WHERE
    gameweek=@gameweek),
  player_point_ordering AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY manager_id, position ORDER BY total_points DESC) 
      AS point_order,
  FROM
    base_cte),
  first_goalie_selection AS (
  SELECT
    *
  FROM
    player_point_ordering
  WHERE
    (point_order = 1)
    AND (position=1) ),
  first_defender_selection AS (
  SELECT
    *
  FROM
    player_point_ordering
  WHERE
    (point_order <= 3)
    AND (position=2) ),
  first_midfield_selection AS (
  SELECT
    *
  FROM
    player_point_ordering
  WHERE
    (point_order <=2)
    AND (position=3) ),
  first_striker_selection AS (
  SELECT
    *
  FROM
    player_point_ordering
  WHERE
    (point_order = 1)
    AND (position=4) ),
  first_selected_players AS (
  SELECT
    * EXCEPT(point_order)
  FROM
    first_goalie_selection
  UNION ALL
  SELECT
    * EXCEPT(point_order)
  FROM
    first_defender_selection
  UNION ALL
  SELECT
    * EXCEPT(point_order)
  FROM
    first_midfield_selection
  UNION ALL
  SELECT
    * EXCEPT(point_order)
  FROM
    first_striker_selection ),
  unselected_defenders AS (
  SELECT
    *
  FROM
    player_point_ordering
  WHERE
    (point_order > 3)
    AND (position=2) ),
  unselected_midfielders AS (
  SELECT
    *
  FROM
    player_point_ordering
  WHERE
    (point_order > 2)
    AND (position=3) ),
  unselected_strikers AS (
  SELECT
    *
  FROM
    player_point_ordering
  WHERE
    (point_order > 1)
    AND (position=4) ),
  unselected_players AS (
  SELECT
    * EXCEPT(point_order)
  FROM
    unselected_defenders
  UNION ALL
  SELECT
    * EXCEPT(point_order)
  FROM
    unselected_midfielders
  UNION ALL
  SELECT
    * EXCEPT(point_order)
  FROM
    unselected_strikers ),
  unselected_players_point_ordering AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY manager_id ORDER BY total_points DESC) 
      AS new_player_order
  FROM
    unselected_players ),
  second_selected_players AS (
  SELECT
    * EXCEPT(new_player_order)
  FROM
    unselected_players_point_ordering
  WHERE
    new_player_order <=4 ),
  best_team AS (
  SELECT
    *
  FROM
    first_selected_players
  UNION ALL
  SELECT
    *
  FROM
    second_selected_players ),
  new_captain_ordering AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY manager_id ORDER BY total_points DESC) 
      AS new_captain,
  FROM
    best_team ),
  new_player_points AS (
  SELECT
    manager_id,
    total_points_with_captain AS new_team_total,
    (CASE
        WHEN new_captain=1 THEN total_points*captaincy_multiplier
      ELSE
      total_points
    END
      ) AS new_team_total_with_new_captain,
  FROM
    new_captain_ordering ),
  new_team_totals AS (
  SELECT
    manager_id,
    SUM(new_team_total) AS `Best Team Total`,
    SUM(new_team_total_with_new_captain) AS `Best Team Total + Captain`
  FROM
    new_player_points
  GROUP BY
    manager_id ),
 original_team_total AS (
  SELECT
    manager_id,
    points,
    points_on_bench
  FROM
    ^
  WHERE
    event = @gameweek )
SELECT
  t1.manager_id,
  t2.points AS `Original Total`,
  (CASE
      WHEN `Best Team Total` < t2.points THEN t2.points
    ELSE
    `Best Team Total`
  END
    ) AS `Best Team Total`,
  (CASE
      WHEN `Best Team Total` < t2.points THEN t2.points + 
        (`Best Team Total + Captain` - `Best Team Total`)
    ELSE
    `Best Team Total + Captain`
  END
    ) AS `Best Team Total + Captain`,
  points_on_bench AS `Points on Bench`,
  (`Best Team Total` - t2.points) as  `Unutilised bench points`,
  @gameweek as `Gameweek`
FROM
  new_team_totals AS t1
INNER JOIN
  original_team_total AS t2
ON
  t1.manager_id = t2.manager_id
ORDER BY `Original Total` DESC
"""
