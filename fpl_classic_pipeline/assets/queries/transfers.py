transfers = """
WITH
  CTE AS (
  SELECT
    manager_id,
    gameweek,
    id,
    full_name,
    total_points,
    COUNT(*) OVER (PARTITION BY manager_id, id ORDER BY gameweek) AS player_freq,
    COUNT(*) OVER (PARTITION BY manager_id, id ORDER BY gameweek DESC) 
      AS player_freq_reverse
  FROM
    $
  WHERE
    (multiplier >0)
    AND ((gameweek=@gameweek)
      OR (gameweek=@gameweek-1))),
  CTE_in AS (
  SELECT
    manager_id,
    STRING_AGG(full_name,', ') AS `players_in`,
    SUM(total_points) AS `points_in`
  FROM
    CTE
  WHERE
    (gameweek=@gameweek)
    AND (player_freq=1)
  GROUP BY
    manager_id ),
  CTE_out AS (
  SELECT
    manager_id,
    gameweek,
    id,
    full_name,
    total_points
  FROM
    CTE
  WHERE
    (gameweek=@gameweek-1)
    AND (player_freq_reverse=1)),
  CTE_out_points AS (
  SELECT
    t1.manager_id,
    STRING_AGG(t1.full_name,', ') AS `players_out`,
    SUM(t2.total_points) AS `points_out`
  FROM
    CTE_out AS t1
  LEFT JOIN
    ^ AS t2
  ON
    t1.id = t2.id
    AND t1.gameweek = t2.gameweek-1
  GROUP BY
    t1.manager_id)
SELECT
  CAST(p_in.manager_id AS int) AS `manager_id`,
  p_in.points_in AS `Points from Players In`,
  p_out.points_out AS `Points from Players Out`,
  p_in.players_in AS `Players Transferred In`,
  p_out.players_out AS `Players Transferred Out`,
  @gameweek as `Gameweek`
FROM
  CTE_in AS p_in
INNER JOIN
  CTE_out_points AS p_out
ON
  p_in.manager_id = p_out.manager_id
"""
