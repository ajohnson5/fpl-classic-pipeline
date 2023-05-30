chip_usage = """
WITH
  active_chips AS (
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
  null_chips AS (
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
  gameweek_chips AS (
  SELECT
    manager_id,
    event AS `Gameweek`,
    points AS `Points`,
    chip AS `Chip`,
    counter
  FROM
    active_chips
  UNION ALL
  SELECT
    manager_id,
    event AS `Gameweek`,
    points AS `Points`,
    chip AS `Chip`,
    counter
  FROM
    null_chips)
SELECT
  *
FROM
  gameweek_chips
ORDER BY
  manager_id
"""
