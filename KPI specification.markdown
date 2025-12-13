# Project KPI Specification

**Project:** <project_name>  
**Owner:** <owner_name>  
**Date:** <YYYY-MM-DD>

## Priority KPIs
- **Revenue lift**
  - **Definition:** Incremental revenue attributable to this project.
  - **Formula:** Revenue_project_period - Revenue_baseline_period
  - **Unit:** USD; % lift vs baseline
  - **Data sources:** Sales system; attribution logs
  - **Target (short-term):** +10% revenue lift
- **Time saved**
  - **Definition:** Reduction in person-hours for the targeted workflow.
  - **Formula:** Baseline_avg_duration - Current_avg_duration
  - **Unit:** Hours saved per task; % reduction
  - **Data sources:** Time tracking; workflow logs
  - **Target (short-term):** 30% reduction
- **Error reduction**
  - **Definition:** Decrease in error rate or rework for the workflow.
  - **Formula:** (Baseline_errors - Current_errors) / Baseline_errors
  - **Unit:** % reduction; errors per 1,000 ops
  - **Data sources:** QA logs; incident tracker
  - **Target (short-term):** 50% reduction

## Baseline collection
- **Period:** 4 weeks (recommended)
- **Required fields:** user_id, workflow_step, start_time, end_time, outcome, error_code, revenue_tag

## Attribution rules
- **Primary method:** Experiment uplift (A/B) where possible; otherwise documented multi-touch rules.
