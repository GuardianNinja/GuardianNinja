SELECT
  cohort_id,
  AVG(baseline_duration_seconds)/3600.0 AS baseline_avg_hours,
  AVG(current_duration_seconds)/3600.0 AS current_avg_hours,
  (AVG(baseline_duration_seconds) - AVG(current_duration_seconds))/3600.0 AS hours_saved
FROM (
  SELECT cohort_id,
         CASE WHEN period='baseline' THEN duration_seconds END AS baseline_duration_seconds,
         CASE WHEN period='current' THEN duration_seconds END AS current_duration_seconds
  FROM workflow_durations
) t
GROUP BY cohort_id;
