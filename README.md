# Teacher Training Data Funnel

Prework for a Data Engineer interview at Labhya (Question 1). The prompt: *"the teams
need to understand how teacher understanding from training translates into classroom
practice quality."* This project builds a dummy dataset for Labhya's two data sources,
derives a training → practice → insight funnel from it, and presents the result as a
dashboard wireframe.

## Project structure

```
plan/       Requirements, dataset design, and analytics design docs (written before code)
scripts/    Python scripts that generate and process the data
data/       Generated CSVs (outputs of the scripts, checked in for review)
dashboard/  Self-contained HTML dashboard wireframe driven by data/
```

### `plan/`
- `q1_requirements.md` — restates the prompt's ask and constraints; no solutioning.
- `q1_dummy_dataset_plan.md` — schema, scale, and edge cases for the dummy dataset.
- `q1_analytics_plan.md` — how training gain and practice change are derived and joined
  into an insight, and what the dashboard shows.

### `scripts/`
- `generate_dummy_data.py` — generates the two raw source tables with seeded RNG,
  writing `data/classroom_observation_tool.csv` and `data/teacher_training_tracker.csv`.
- `build_analytics.py` — reads those two CSVs and derives `data/teacher_analytics.csv`
  (one row per teacher: training gain, pre/post practice scores, delta, status flags,
  quadrant) and `data/funnel_summary.csv` (funnel stage counts).

### `data/`
Generated, not hand-authored — regenerate by re-running the scripts (see below).

### `dashboard/`
`training_practice_dashboard.html` — a self-contained HTML wireframe (no build step)
visualizing the funnel and quadrant analysis from `data/`. Open directly in a browser.

## Running the pipeline

Requires Python 3 with `pandas` and `numpy`.

```bash
python3 scripts/generate_dummy_data.py   # writes the two raw CSVs to data/
python3 scripts/build_analytics.py       # derives teacher_analytics.csv + funnel_summary.csv
```

Then open `dashboard/training_practice_dashboard.html` in a browser.

## Data model

Two source tables, linked only by `teacher_id` (no school hierarchy in this dataset):

- **Classroom Observation Tool** — one row per observation visit, scored 1–5 on lesson
  plan, execution, student engagement, and classroom management.
- **Teacher Training Tracker** — one row per teacher, wide baseline/endline (BL/EL) pairs
  for knowledge, skill, and attitude, scored 1–5.

The dummy data deliberately injects timing gaps, missing endline scores, and an
unmatched `teacher_id` so the analytics and dashboard have real data-quality issues to
surface rather than a clean, unrealistic sample — see `plan/q1_dummy_dataset_plan.md` for
the full list of injected edge cases.
