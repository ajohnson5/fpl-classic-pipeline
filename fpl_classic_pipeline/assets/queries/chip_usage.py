chip_usage = """
WITH
  CTE AS (
  SELECT
    manager_id,
    event,
    points,
    CAST(chip AS STRING) as `chip`,
    1/COUNT(*) OVER (PARTITION BY event ) AS counter
  FROM
    $
  WHERE
    chip IS NOT NULL
    AND event = @gameweek),
  CTE2 AS (
  SELECT
    manager_id,
    event,
    points,
    'None' AS chip,
    0 AS counter
  FROM
    $
  WHERE
    chip IS NULL
    AND event = @gameweek),
  CTE3 AS (
  SELECT
    manager_id,
    event AS `Gameweek`,
    points AS `Points`,
    chip AS `Chip`,
    counter
  FROM
    CTE
  UNION ALL
  SELECT
    manager_id,
    event AS `Gameweek`,
    points AS `Points`,
    chip AS `Chip`,
    counter
  FROM
    CTE2)
SELECT
  *
FROM
  CTE3
ORDER BY
  manager_id
"""
