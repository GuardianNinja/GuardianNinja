# KPI_SPEC.md

**Project:** Women's Lab Edition  
**Owner:** LEIF  
**Date:** 2025-12-13

---

## Purpose
This document formalizes the project’s priority KPIs, measurement approach, instrumentation requirements, baseline collection plan, attribution rules, pilot timeline, and reporting cadence. The goal is to ensure every change is evaluated against **Revenue lift**, **Time saved**, and **Error reduction** so decisions are data driven.

---

## Priority KPIs

### Revenue lift
- **Definition:** Incremental revenue attributable to this project during the measurement period.  
- **Formula:** `Revenue_project_period - Revenue_baseline_period`  
- **Unit:** USD; percent lift vs baseline  
- **Data sources:** Sales system; attribution logs; payment gateway events  
- **Short-term target:** **+10%** revenue lift vs baseline  
- **Notes:** Use experiment uplift where possible; otherwise document multi-touch attribution rules.

### Time saved
- **Definition:** Reduction in person-hours required to complete the targeted workflow.  
- **Formula:** `Baseline_avg_duration - Current_avg_duration`  
- **Unit:** Hours saved per task; percent reduction  
- **Data sources:** Time tracking; workflow logs; automated timestamps from the system  
- **Short-term target:** **30%** reduction in average task duration

### Error reduction
- **Definition:** Decrease in error rate or rework for the targeted workflow.  
- **Formula:** `(Baseline_errors - Current_errors) / Baseline_errors`  
- **Unit:** Percent reduction; errors per 1,000 operations  
- **Data sources:** QA logs; incident tracker; automated error codes from services  
- **Short-term target:** **50%** reduction in error rate

---

## Baseline Collection
- **Recommended baseline period:** 4 weeks (use historical 4-week window if representative).  
- **Minimum baseline period:** 2 weeks if time constrained.  
- **Required baseline fields:** `user_id`, `workflow_step`, `start_time`, `end_time`, `outcome`, `error_code`, `revenue_tag`, `cohort_id`.  
- **Data quality checks before baseline acceptance:** completeness > 98%; no duplicate event IDs; timestamp sanity (start < end).

---

## Instrumentation Requirements
- **Events to log for every workflow instance:**  
  - `event_id` (unique)  
  - `user_id` (anonymized if PII concerns)  
  - `project_id`  
  - `cohort_id` (control/variant)  
  - `workflow_step`  
  - `start_time` (ISO 8601)  
  - `end_time` (ISO 8601)  
  - `duration_seconds` (computed)  
  - `outcome` (success/failure)  
  - `error_code` (nullable)  
  - `revenue_tag` (nullable; USD value when applicable)  
  - `metadata` (JSON blob for contextual fields)

- **Logging standards:** consistent field names; UTC timestamps; no PII in metrics tables; use hashed IDs if needed.

---

## Attribution Rules
- **Primary method:** Experiment uplift (A/B) with randomized assignment and parallel cohorts.  
- **Fallback method:** Documented multi-touch attribution (last-touch by default unless product team specifies otherwise).  
- **Revenue attribution:** Tag revenue events with `revenue_tag` and link to `event_id` or `cohort_id`. For subscription or delayed revenue, use an attribution window (e.g., 30 days) and document it.

---

## Pilot Design and Statistical Approach
- **Pilot type:** A/B test or phased rollout depending on operational constraints.  
- **Cohorts:** Control and one or more variants; minimum cohort size determined by power calculation.  
- **Duration:** 6–8 weeks recommended (includes baseline and pilot).  
- **Statistical tests:**  
  - **Revenue lift:** two-sample t-test or nonparametric equivalent on per-user revenue; bootstrap for skewed revenue.  
  - **Time saved:** t-test on durations; log-transform if distribution is skewed.  
  - **Error reduction:** chi-square or Fisher exact test on error counts.  
- **Success criteria:** pre-specified thresholds for each KPI and p-value or confidence interval rules documented in the experiment plan.

---

## Pilot Timeline (6–8 week example)
- **Week 0:** Finalize KPI_SPEC.md, instrument events, assign owners, run data quality checks.  
- **Weeks 1–2:** Collect baseline data (or validate historical baseline).  
- **Weeks 3–6:** Run pilot (A/B or phased rollout). Monitor daily for data integrity and safety issues.  
- **Week 7:** Aggregate metrics, run statistical tests, validate results.  
- **Week 8:** Draft case study, executive snapshot, and scaling recommendation.

---

## Minimal Metrics Table Schema
- **Table name:** `project_metrics`  
- **Columns:**  
  - `date` (DATE)  
  - `project_id` (STRING)  
  - `cohort_id` (STRING)  
  - `kpi_name` (STRING)  
  - `value` (FLOAT)  
  - `baseline_value` (FLOAT)  
  - `n` (INT)  
  - `notes` (STRING)

---

## Sample SQL Snippets

### Compute average duration and hours saved by cohort
```sql
SELECT
  cohort_id,
  AVG(baseline_duration_seconds)/3600.0 AS baseline_avg_hours,
  AVG(current_duration_seconds)/3600.0 AS current_avg_hours,
  (AVG(baseline_duration_seconds) - AVG(current_duration_seconds))/3600.0 AS hours_saved
FROM workflow_durations
GROUP BY cohort_id;
