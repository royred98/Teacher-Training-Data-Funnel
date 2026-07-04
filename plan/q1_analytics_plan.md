# Q1 — Analytics Derivation Plan (Training → Practice → Insight)

## Context

This plan defines how analytics are derived from the two data sources — Teacher Training
Tracker and Classroom Observation Tool (per `plan/q1_dummy_dataset_plan.md`) — to answer the
real question: *does training that builds a teacher's KSA actually translate to better
classroom practice?* It resolves the two items left open in `plan/q1_requirements.md` (§5):
the timing rule for "post-training practice" and what "insight" concretely means.

**Dependency, tracked separately:** this analytics design needs the Classroom Observation
Tool to provide a pre-training baseline visit for most teachers (mirroring the BL/EL
structure already used on the training side), not just a rare edge case. That dataset change
is being planned in `plan/q1_dummy_dataset_plan.md`, not here — this document only assumes
the resulting data shape (each teacher may or may not have a pre-training score, and may or
may not have post-training scores) and works from whatever flags that produces.

Dataset stays teacher-level only (no school hierarchy), so analytics/dashboard operate at
whole-program level + a teacher-level list, no drill-down.

## Data Flow: Training → Practice → Insight

```
Teacher Training Tracker ──▶ Layer 1: Training Gain ────┐
                                                          ├──▶ Layer 3: Join + Quadrant ──▶ Dashboard
Classroom Observation Tool ─▶ Layer 2: Practice Pre/Post ┘
```

### Layer 1 — Training Gain (from Teacher Training Tracker, per teacher)
- `knowledge_gain = knowledge_score_el − knowledge_score_bl` (same for skill, attitude)
- `composite_training_gain` = mean of the three gain scores
- `assessment_incomplete` = true when EL scores are null → excluded from gain calc, shown
  as its own status rather than treated as zero gain

### Layer 2 — Practice Pre/Post (from Classroom Observation Tool, per teacher)
- `pre_training_practice_score` = composite (mean of the 4 indicators) of the teacher's
  pre-training visit, if present
- `post_training_practice_score` = mean of per-visit composites across the teacher's valid
  post-training visits (`obs_date > training_date`), if any
- `practice_delta = post_training_practice_score − pre_training_practice_score`, computed
  only when **both** exist
- Status flags (visible, not collapsed into a single "missing" bucket):
  - `no_baseline` — post score exists, no pre score → no delta, absolute post-score only
  - `no_post_observation` — pre score exists, no post visit → can't tell if training
    changed anything on the ground yet
  - `pending_observation` — neither exists
  - `no_training_record` — observed but no training row at all — excluded from this table,
    counted separately as a data-integrity issue

### Layer 3 — Join & Insight Classification
Outer join Layer 1 + Layer 2 on `teacher_id`. Primary insight axis is **change**, not just
level: does a KSA gain from training show up as a practice gain?
- `composite_training_gain ≥ 1.0` (of 5) = "high gain"
- `practice_delta ≥ 0.5` = "meaningful practice improvement"

| | Practice improved | Flat / declined |
|---|---|---|
| **High training gain** | Training Translating Well | **Knowing-Doing Gap** → coaching/follow-up, not re-training |
| **Low training gain** | Improvement from other factors (worth investigating — training may not be the driver) | Needs Foundational Support → re-training candidate |

Only computed for teachers with both `composite_training_gain` and `practice_delta`
available (i.e. not `assessment_incomplete`, `no_baseline`, `no_post_observation`, or
`pending_observation`). Everyone else still shows up in the dashboard's data-health view —
e.g. a "no_baseline" teacher still shows their absolute post-training practice score even
without a delta, so they're not invisible, just not quadrant-classified.

Fixed thresholds (not cohort-relative medians) are used so the bar stays stable across
training cycles.

## Dashboard Consumption

- **Top tiles:** % assessed complete · % with both pre & post observation (delta-ready) ·
  avg composite training gain · avg practice delta · count/% "Knowing-Doing Gap" · data-health
  flag count
- **Funnel chart:** Trained → Assessed → Baseline Observed → Post-Training Observed →
  Delta-ready (Insight-ready), showing drop-off per stage
- **Scatter plot:** composite training gain (x) vs practice delta (y), quadrant-shaded,
  one point per teacher, hover shows teacher_id + flags + absolute pre/post scores
- **Quadrant summary:** bar/count per quadrant
- **Sortable/filterable teacher table:** teacher_id, training gain, pre/post practice
  scores, delta, quadrant, flags — filterable to e.g. "Knowing-Doing Gap"
- **Data-health panel:** explicit list of pending / no-baseline / no-follow-up /
  no-training-record teachers, kept visible rather than averaged away

## Implementation Approach

1. Once the dataset update in `plan/q1_dummy_dataset_plan.md` is executed, build
   `scripts/build_analytics.py`: reads the two CSVs, computes Layers 1–3, writes
   `data/teacher_analytics.csv` (one row per teacher: gain fields, pre/post practice scores,
   delta, flags, quadrant) and `data/funnel_summary.csv` (stage counts) — the dashboard's
   data source.
2. Dashboard: a self-contained HTML artifact (visual wireframe, per earlier decision) driven
   by these derived CSVs — built once this logic is approved and validated.

## Verification

- Recompute funnel/quadrant counts against the (updated) dataset and confirm a meaningful
  number of teachers are delta-ready, plus non-trivial counts in each data-health flag.
- Confirm every edge case surfaces as a distinct, visible status in
  `teacher_analytics.csv` rather than being dropped or silently averaged in.
