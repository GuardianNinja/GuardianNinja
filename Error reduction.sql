WITH baseline AS (
  SELECT cohort_id, COUNT(*) AS baseline_total, SUM(CASE WHEN error_code IS NOT NULL THEN 1 ELSE 0 END) AS baseline_errors
  FROM workflow_events
  WHERE period = 'baseline'
  GROUP BY cohort_id
),
current AS (
  SELECT cohort_id, COUNT(*) AS current_total, SUM(CASE WHEN error_code IS NOT NULL THEN 1 ELSE 0 END) AS current_errors
  FROM workflow_events
  WHERE period = 'current'
  GROUP BY cohort_id
)
SELECT
  b.cohort_id,
  (b.baseline_errors::float / b.baseline_total) AS baseline_error_rate,
  (c.current_errors::float / c.current_total) AS current_error_rate,
  CASE WHEN b.baseline_errors = 0 THEN NULL ELSE ((b.baseline_errors - c.current_errors) / b.baseline_errors) END AS error_reduction_pct
FROM baseline b
JOIN current c ON b.cohort_id = c.cohort_id;
