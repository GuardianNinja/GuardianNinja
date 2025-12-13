INSERT INTO project_metrics (date, project_id, cohort_id, kpi_name, value, baseline_value, n, notes)
SELECT
  CURRENT_DATE AS date,
  'womens_lab_edition' AS project_id,
  cohort_id,
  'revenue_per_user' AS kpi_name,
  SUM(COALESCE(revenue_tag,0)) / NULLIF(COUNT(DISTINCT user_id),0) AS value,
  NULL AS baseline_value,
  COUNT(DISTINCT user_id) AS n,
  'daily ingestion'
FROM workflow_events
WHERE event_time >= CURRENT_DATE - INTERVAL '1 day'
GROUP BY cohort_id;
