manager_rank = """
SELECT
  manager_id,
  event as Gameweek,
  RANK() OVER (PARTITION BY event ORDER BY total_points DESC, manager_id ASC) AS Rank
FROM
  $
WHERE
  event = @gameweek
"""
