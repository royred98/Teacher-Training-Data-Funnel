"""Derive the Training -> Practice -> Insight analytics table (Q1 analytics plan).

Reads the two raw CSVs and writes:
  - data/teacher_analytics.csv  (one row per teacher: training gain, pre/post practice,
    delta, status flags, quadrant)
  - data/funnel_summary.csv     (stage-by-stage counts for the funnel chart)
"""

import os

import numpy as np
import pandas as pd

HIGH_GAIN_THRESHOLD = 1.0
HIGH_DELTA_THRESHOLD = 0.5

OBS_INDICATOR_COLS = [
    "lesson_plan_score", "execution_score",
    "student_engagement_score", "classroom_management_score",
]


def load_data(data_dir):
    tr = pd.read_csv(os.path.join(data_dir, "teacher_training_tracker.csv"))
    obs = pd.read_csv(os.path.join(data_dir, "classroom_observation_tool.csv"))
    return tr, obs


def build_layer1_training_gain(tr):
    tr = tr.copy()
    tr["knowledge_gain"] = tr["knowledge_score_el"] - tr["knowledge_score_bl"]
    tr["skill_gain"] = tr["skill_score_el"] - tr["skill_score_bl"]
    tr["attitude_gain"] = tr["attitude_score_el"] - tr["attitude_score_bl"]
    tr["composite_training_gain"] = tr[["knowledge_gain", "skill_gain", "attitude_gain"]].mean(axis=1)
    tr["assessment_incomplete"] = tr["knowledge_score_el"].isna()
    return tr[[
        "teacher_id", "date", "composite_training_gain", "assessment_incomplete",
        "knowledge_gain", "skill_gain", "attitude_gain",
    ]].rename(columns={"date": "training_date"})


def build_layer2_practice(training_dates_df, obs):
    merged = obs.merge(training_dates_df, on="teacher_id", how="left")

    merged["no_training_record"] = merged["training_date"].isna()
    merged["obs_composite"] = merged[OBS_INDICATOR_COLS].mean(axis=1)
    merged["is_pre_training"] = (~merged["no_training_record"]) & (merged["date"] <= merged["training_date"])
    merged["is_post_training"] = (~merged["no_training_record"]) & (merged["date"] > merged["training_date"])

    # Data-integrity issue: observed but no training record — reported separately, not
    # part of the teacher-level analytics table.
    unmatched = merged.loc[merged["no_training_record"], "teacher_id"].unique().tolist()

    matched = merged[~merged["no_training_record"]]

    pre_score = (
        matched[matched["is_pre_training"]]
        .groupby("teacher_id")["obs_composite"].mean()
        .rename("pre_training_practice_score")
    )
    post_score = (
        matched[matched["is_post_training"]]
        .groupby("teacher_id")["obs_composite"].mean()
        .rename("post_training_practice_score")
    )
    post_visit_count = (
        matched[matched["is_post_training"]]
        .groupby("teacher_id").size()
        .rename("post_visit_count")
    )

    practice = pd.concat([pre_score, post_score, post_visit_count], axis=1).reset_index()
    return practice, unmatched


def build_layer3_analytics(tr_ids, layer1, layer2):
    analytics = pd.DataFrame({"teacher_id": tr_ids}).merge(layer1, on="teacher_id", how="left")
    analytics = analytics.merge(layer2, on="teacher_id", how="left")

    analytics["practice_delta"] = (
        analytics["post_training_practice_score"] - analytics["pre_training_practice_score"]
    )

    has_pre = analytics["pre_training_practice_score"].notna()
    has_post = analytics["post_training_practice_score"].notna()

    analytics["no_baseline"] = (~has_pre) & has_post
    analytics["no_post_observation"] = has_pre & (~has_post)
    analytics["pending_observation"] = (~has_pre) & (~has_post)
    analytics["single_post_visit"] = analytics["post_visit_count"] == 1

    insight_ready = (
        (~analytics["assessment_incomplete"])
        & has_pre & has_post
    )

    high_gain = analytics["composite_training_gain"] >= HIGH_GAIN_THRESHOLD
    high_delta = analytics["practice_delta"] >= HIGH_DELTA_THRESHOLD

    conditions = [
        insight_ready & high_gain & high_delta,
        insight_ready & high_gain & ~high_delta,
        insight_ready & ~high_gain & ~high_delta,
        insight_ready & ~high_gain & high_delta,
    ]
    choices = [
        "Training Translating Well",
        "Knowing-Doing Gap",
        "Needs Foundational Support",
        "Improvement from Other Factors",
    ]
    analytics["quadrant"] = np.select(conditions, choices, default="Not Insight-Ready")

    return analytics


def build_funnel_summary(analytics, n_trained, n_unmatched):
    n_assessed = (~analytics["assessment_incomplete"]).sum()
    n_baseline_observed = analytics["pre_training_practice_score"].notna().sum()
    n_post_observed = analytics["post_training_practice_score"].notna().sum()
    n_insight_ready = (analytics["quadrant"] != "Not Insight-Ready").sum()

    return pd.DataFrame([
        {"stage": "Trained", "count": n_trained},
        {"stage": "Assessed (BL+EL complete)", "count": int(n_assessed)},
        {"stage": "Baseline Observed", "count": int(n_baseline_observed)},
        {"stage": "Post-Training Observed", "count": int(n_post_observed)},
        {"stage": "Insight-Ready (delta computed)", "count": int(n_insight_ready)},
        {"stage": "Unmatched teacher_id (data-integrity)", "count": n_unmatched},
    ])


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    tr, obs = load_data(data_dir)
    layer1 = build_layer1_training_gain(tr)
    layer2, unmatched = build_layer2_practice(layer1[["teacher_id", "training_date"]], obs)

    analytics = build_layer3_analytics(tr["teacher_id"].tolist(), layer1, layer2)
    funnel = build_funnel_summary(analytics, n_trained=len(tr), n_unmatched=len(unmatched))

    analytics_path = os.path.join(data_dir, "teacher_analytics.csv")
    funnel_path = os.path.join(data_dir, "funnel_summary.csv")
    analytics.to_csv(analytics_path, index=False)
    funnel.to_csv(funnel_path, index=False)

    print(funnel.to_string(index=False))
    print()
    print("Quadrant counts:")
    print(analytics["quadrant"].value_counts().to_string())
    print()
    print(f"Unmatched teacher_id(s) (no training record): {unmatched}")


if __name__ == "__main__":
    main()
