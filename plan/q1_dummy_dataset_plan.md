# Q1 — Dummy Dataset Creation Plan

## Context

Following the requirements/context capture in `plan/q1_requirements.md` (in the project
folder), we're now solutioning the first deliverable: the actual dummy dataset for the two
Labhya data sources. This plan fixes the schema, scale, and generation approach so the next
step is just running a script — no more open schema decisions.

Scope for this dataset: **50 teachers**, each with **2–3 Classroom Observation entries**
and **exactly 1 Teacher Training Tracker entry**. Data is kept at the **teacher level only**
— no school master or school join. `teacher_id` is the sole key linking the two tables to
each other; there is no organizational hierarchy above it in this dataset.

## Schema

### Classroom Observation Tool (user-specified fields, kept as given)
`sl_no`, `observer_id`, `teacher_id`, `date`,
`lesson_plan_score`, `execution_score`, `student_engagement_score`,
`classroom_management_score` — each scored **1–5**.
- 2–3 rows per teacher → ~120–135 rows total.
- `observer_id` drawn from a pool of ~10 observer IDs (no separate observer table needed
  at this scale — it's just an ID value, not a joined entity).
- No stored composite/overall score — an overall practice score is a derived value for the
  funnel stage, not raw data, so it won't be generated here.

### Teacher Training Tracker (user-specified `sl_no`, `teacher_id`, `date`; scores suggested below)
`sl_no`, `teacher_id`, `date` (training date), plus BL/EL score pairs — one row per
teacher, wide format (BL and EL side by side) since the user confirmed 1 entry/teacher:
- `knowledge_score_bl`, `knowledge_score_el` — SEL concept/content test
- `skill_score_bl`, `skill_score_el` — practical/facilitation demonstration scored by trainer
- `attitude_score_bl`, `attitude_score_el` — self-reported Likert survey on SEL beliefs/confidence

All on the same **1–5** scale as the observation tool, so scores are comparable across
sources later. 50 rows, one per teacher.

`teacher_id` values (e.g. `T001`–`T050`) are shared across both tables and are the only
linkage between them — no other master/reference table is generated.

## Realism & Edge Cases to Inject

Per the timing/missing-data/inconsistency handling already flagged as open in
`q1_requirements.md`, the generated data should contain real instances of each issue rather
than being clean:
- **Missing EL scores** for ~3 teachers (simulates incomplete endline assessment).
- **Zero observations** for 1 teacher, and **only 1 observation** (instead of 2–3) for 2
  teachers (simulates monitoring/coverage gaps).
- **1–2 observation dates that fall before the teacher's training date** (edge case for
  later "post-training practice" window logic).
- **1 `teacher_id` present in the Observation Tool but absent from the Training Tracker**
  (simulates a teacher observed without a matching training record — a cross-table
  inconsistency between the two systems, since there's no master table to reconcile
  against).
- Observation scores loosely correlated with each teacher's EL scores plus random noise
  (not pure random), so later funnel/quadrant analysis has real signal to show.

## Generation Approach

One Python script (`pandas` + `numpy`, seeded RNG for reproducibility) producing 2 CSVs
into a new `data/` folder at the project root:
- `data/classroom_observation_tool.csv`
- `data/teacher_training_tracker.csv`

Dates: training dates spread across a plausible window (e.g. Jun–Jul 2025), observation
dates mostly after each teacher's training date through ~Nov 2025 (with the 1–2 pre-training
exceptions above).

## Verification

- Run the script; confirm row counts match spec (50 training rows, ~120–135 observation
  rows).
- Spot-check the `teacher_id` linkage: every teacher in the Training Tracker has 0, 1, or
  2–3 matching observation rows as intended; confirm the one deliberately unmatched
  `teacher_id` case is present.
- Confirm each injected edge case is present and easy to locate (e.g. via a quick
  `pandas` filter) for use as a demonstration in the written answer.
