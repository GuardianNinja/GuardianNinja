SELECT
  cohort,
  AVG(baseline_duration) AS baseline_avg,
  AVG(current_duration) AS current_avg,
  (AVG(baseline_duration) - AVG(current_duration)) AS hours_saved
FROM workflow_durations
GROUP BY cohort;
