summary_stats = """
  WITH 
    CTE_min_points AS (
  SELECT
    'Fewest Points in a Gameweek' AS Statistic,
    MIN(points) AS `Value`
  FROM
    $
  WHERE
    event <= @gameweek and event!=7
  GROUP BY
    manager_id
  ORDER BY
    `Value` ASC
  LIMIT
    1 ),
  CTE_max_points AS (
  SELECT
    'Most Points in a Gameweek' AS Statistic,
    MAX(points) AS `Value`
  FROM
    $
  WHERE
    event <= @gameweek
  GROUP BY
    manager_id
  ORDER BY
    `Value` DESC
  LIMIT
    1 ),
  CTE_min_captain AS (
  SELECT
    'Fewest Total Points from Captains' AS Statistic,
    SUM(actual_points) AS Value
  FROM
    ^
  WHERE
    (multiplier > 1 )and 
    (gameweek <= @gameweek)
  GROUP BY
    manager_id
  ORDER BY
    Value ASC
  LIMIT
    1),
  CTE_max_captain AS (
  SELECT
    'Greatest Total Points from Captains' AS Statistic,
    SUM(actual_points) AS Value
  FROM
    ^
  WHERE
    (multiplier > 1 )and 
    (gameweek <= @gameweek)
  GROUP BY
    manager_id
  ORDER BY
    Value DESC
  LIMIT
    1),
  CTE_dreamteam AS (
  SELECT
    'Most players in the Dreamteam' AS Statistic,
    COUNT(CASE
        WHEN in_dreamteam= TRUE THEN 1
    END
      ) AS Value
  FROM
    ^
  WHERE
    gameweek <= @gameweek
  GROUP BY
    manager_id
  ORDER BY
    Value DESC
  LIMIT
    1 ),
  CTE_max_bonus AS (
  SELECT
    'Greatest Total Bonus Points' AS Statistic,
    SUM(bonus) AS Value
  FROM
    ^
  WHERE
    gameweek <= @gameweek
  GROUP BY
    manager_id
  ORDER BY
    manager_id DESC
  LIMIT
    1 ),
      CTE_max_yellow AS (
  SELECT
    'Most Yellow Cards in Total' AS Statistic,
    SUM(yellow_cards) AS `Value`
  FROM
    ^
  WHERE
    gameweek <= @gameweek
  GROUP BY
    manager_id
  ORDER BY
    `Value` DESC
  LIMIT
    1 ),
      CTE_max_bench_points AS (
  SELECT
    'Most Points on the Bench' AS Statistic,
    SUM(points_on_bench) AS `Value`
  FROM
    $
  WHERE
    event <= @gameweek
  GROUP BY
    manager_id
  ORDER BY
    `Value` DESC
  LIMIT
    1 ),
      CTE_max_transfer_cost AS (
  SELECT
    'Highest Total Transfer Cost' AS Statistic,
    SUM(event_transfers_cost) AS `Value`
  FROM
    $
  WHERE
    event <= @gameweek
  GROUP BY
    manager_id
  ORDER BY
    `Value` DESC
  LIMIT
    1 ),
      CTE_max_haaland AS (
  SELECT
    'Most times a manager captained Erling Haaland' AS `Statistic`,
    COUNT(*) AS `Value`
  FROM
    ^
  WHERE
    full_name='Erling Haaland'
    AND multiplier > 1
    AND gameweek <= @gameweek
  GROUP BY
    manager_id
  ORDER BY
    `Value` DESC
  LIMIT
    1)
SELECT
  *
FROM
  CTE_min_points
UNION ALL
SELECT
  *
FROM
  CTE_max_points
UNION ALL
SELECT
  *
FROM
  CTE_min_captain
UNION ALL
SELECT
  *
FROM
  CTE_max_captain
UNION ALL
SELECT
  *
FROM
  CTE_dreamteam
UNION ALL
SELECT
  *
FROM
  CTE_max_bonus
UNION ALL
SELECT
  *
FROM
  CTE_max_yellow
UNION ALL
SELECT
  *
FROM
  CTE_max_bench_points
UNION ALL
SELECT
  *
FROM
  CTE_max_transfer_cost
UNION ALL
SELECT
  *
FROM
  CTE_max_haaland
"""
