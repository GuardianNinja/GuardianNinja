WITH baseline AS (
  SELECT cohort_id, SUM(COALESCE(revenue_tag,0)) AS baseline_revenue, COUNT(DISTINCT user_id) AS baseline_users
  FROM workflow_events
  WHERE period = 'baseline'
  GROUP BY cohort_id
),
current AS (
  SELECT cohort_id, SUM(COALESCE(revenue_tag,0)) AS current_revenue, COUNT(DISTINCT user_id) AS current_users
  FROM workflow_events
  WHERE period = 'current'
  GROUP BY cohort_id
)
SELECT
  c.cohort_id,
  c.current_revenue,
  b.baseline_revenue,
  (c.current_revenue - b.baseline_revenue) AS revenue_lift_usd,
  CASE WHEN b.baseline_revenue = 0 THEN NULL ELSE (c.current_revenue - b.baseline_revenue) / b.baseline_revenue END AS revenue_lift_pct
FROM current c
JOIN baseline b ON c.cohort_id = b.cohort_id;
