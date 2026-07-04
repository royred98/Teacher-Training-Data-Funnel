"""Generate dummy datasets for Q1: Classroom Observation Tool + Teacher Training Tracker.

Produces two teacher-level CSVs linked only by `teacher_id`, with deliberately
injected timing/missing-data/inconsistency edge cases (see plan/q1_requirements.md).
"""

import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N_TEACHERS = 50
TEACHER_IDS = [f"T{i:03d}" for i in range(1, N_TEACHERS + 1)]

MISSING_EL_TEACHERS = {"T007", "T023", "T041"}
ZERO_OBS_TEACHER = "T015"
ONE_OBS_TEACHERS = {"T032", "T048"}
UNMATCHED_TEACHER_ID = "T051"  # observed, but has no training record at all

OBSERVER_POOL = [f"OBS{i:02d}" for i in range(1, 11)]

SCORE_COLS = [
    "knowledge_score_bl", "knowledge_score_el",
    "skill_score_bl", "skill_score_el",
    "attitude_score_bl", "attitude_score_el",
]


def random_date(start: date, end: date) -> date:
    span = (end - start).days
    return start + timedelta(days=int(rng.integers(0, span + 1)))


def clip_score(x: float) -> int:
    return int(np.clip(round(x), 1, 5))


def build_training_tracker():
    rows = []
    training_date = {}
    el_avg = {}

    training_start, training_end = date(2025, 6, 1), date(2025, 7, 31)

    for i, tid in enumerate(TEACHER_IDS, start=1):
        t_date = random_date(training_start, training_end)
        training_date[tid] = t_date

        knowledge_bl = clip_score(rng.normal(2.5, 0.8))
        skill_bl = clip_score(rng.normal(2.3, 0.8))
        attitude_bl = clip_score(rng.normal(2.8, 0.8))

        knowledge_el = clip_score(knowledge_bl + rng.normal(1.2, 0.7))
        skill_el = clip_score(skill_bl + rng.normal(1.0, 0.7))
        attitude_el = clip_score(attitude_bl + rng.normal(0.8, 0.7))

        if tid in MISSING_EL_TEACHERS:
            knowledge_el = skill_el = attitude_el = np.nan
            el_avg[tid] = None
        else:
            el_avg[tid] = float(np.mean([knowledge_el, skill_el, attitude_el]))

        rows.append({
            "sl_no": i,
            "teacher_id": tid,
            "date": t_date.isoformat(),
            "knowledge_score_bl": knowledge_bl,
            "knowledge_score_el": knowledge_el,
            "skill_score_bl": skill_bl,
            "skill_score_el": skill_el,
            "attitude_score_bl": attitude_bl,
            "attitude_score_el": attitude_el,
        })

    df = pd.DataFrame(rows)
    df[SCORE_COLS] = df[SCORE_COLS].astype("Int64")
    return df, training_date, el_avg


def make_observation(sl_no, tid, obs_date, teacher_el_avg):
    base = rng.normal(3.0, 0.9) if teacher_el_avg is None else teacher_el_avg + rng.normal(0, 0.6)
    return {
        "sl_no": sl_no,
        "observer_id": OBSERVER_POOL[int(rng.integers(0, len(OBSERVER_POOL)))],
        "teacher_id": tid,
        "date": obs_date.isoformat(),
        "lesson_plan_score": clip_score(base + rng.normal(0, 0.5)),
        "execution_score": clip_score(base + rng.normal(0, 0.5)),
        "student_engagement_score": clip_score(base + rng.normal(0, 0.5)),
        "classroom_management_score": clip_score(base + rng.normal(0, 0.5)),
    }


def build_observation_tool(training_date, el_avg):
    rows = []
    sl_no = 1
    obs_window_end = date(2025, 11, 30)

    pre_training_pool = [t for t in TEACHER_IDS if t not in ({ZERO_OBS_TEACHER} | ONE_OBS_TEACHERS)]
    pre_training_edge_teachers = set(rng.choice(pre_training_pool, size=2, replace=False))

    for tid in TEACHER_IDS:
        if tid == ZERO_OBS_TEACHER:
            continue

        n_obs = 1 if tid in ONE_OBS_TEACHERS else int(rng.integers(2, 4))
        t_date = training_date[tid]

        for k in range(n_obs):
            if k == 0 and tid in pre_training_edge_teachers:
                obs_date = t_date - timedelta(days=int(rng.integers(5, 30)))
            else:
                obs_date = random_date(t_date + timedelta(days=14), obs_window_end)
            rows.append(make_observation(sl_no, tid, obs_date, el_avg[tid]))
            sl_no += 1

    # Cross-table inconsistency: teacher observed but never appears in the training tracker
    for _ in range(2):
        obs_date = random_date(date(2025, 8, 1), obs_window_end)
        rows.append(make_observation(sl_no, UNMATCHED_TEACHER_ID, obs_date, None))
        sl_no += 1

    return pd.DataFrame(rows)


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)

    training_df, training_date, el_avg = build_training_tracker()
    obs_df = build_observation_tool(training_date, el_avg)

    training_df.to_csv(os.path.join(out_dir, "teacher_training_tracker.csv"), index=False)
    obs_df.to_csv(os.path.join(out_dir, "classroom_observation_tool.csv"), index=False)

    print(f"Teacher Training Tracker: {len(training_df)} rows")
    print(f"Classroom Observation Tool: {len(obs_df)} rows")


if __name__ == "__main__":
    main()
