# Q1 — Requirements & Context (Teacher Training → Classroom Practice Data Funnel)

## Context

This is prework for a Data Engineer interview at Labhya. Question 1's underlying goal,
per the prompt: *"the teams need to understand how teacher understanding from training
translates into classroom practice quality."* This document only restates and organizes
what the question explicitly asks for and the facts/constraints it gives us — no
solutioning yet. It exists so the next phase (actually designing the dataset, funnel, and
dashboard) has a clear, agreed-on spec of the ask to work from.

---

## 1. The Two Named Data Sources (as described in the prompt)

**1. Classroom Observation Tool**
- Used by observers to assess classroom practices and quality of implementation.
- Example dimensions given: delivery quality, student engagement, adherence to lesson
  structure.

**2. BL/EL Teacher Training Data**
- Collected during or after training.
- Assesses teachers' knowledge, skills, and attitudes related to SEL.
- **Confirmed by user**: BL/EL = Baseline/Endline. This tool captures the *effectiveness
  of the training administered* to teachers — it indicates the competency the teacher has
  shown (i.e., a pre/post measure of the training's impact on the teacher, not a one-off
  test).

---

## 2. Explicit Deliverables Requested by Question 1

1. Create a **dummy dataset** for these two data sources.
2. Use it to design a **data funnel** that links teacher training to classroom practice
   quality.
3. Using that funnel, outline a **preliminary dashboard UI** that would help program or
   state teams identify where support is needed.
4. In the written response, briefly describe (four required points, verbatim from the
   prompt):
   - The structure of the dummy data (key fields, levels, and relationships)
   - How the data flows through the funnel from training → practice → insight
   - How timing, missing data, or inconsistencies are handled
   - What the dashboard shows (key metrics/visuals) and how it supports decisions

---

## 3. Constraints / Facts Given Elsewhere in the Prework (relevant context)

From Question 2's dataset description, which we're choosing to align Q1 with for
continuity across the submission:
- Labhya operates across **500 partner schools in Tripura**.
- Each school has an assigned **visit frequency** (column C) governing how often
  observations occur there.
- Schools are one of two types (column D): **Vidyajyoti** (Mon–Fri) or **Regular**
  (Mon–Sat).

These are facts about the program's real scale/structure, not requirements of Question 1
itself — but they're available context we can draw the dummy data's school/observation
scale from, per the decision below.

---

## 4. Decisions Already Confirmed With the User (scope for next phase, not solutions)

- The dummy dataset will be produced as **real generated data files** (e.g. CSV via
  script), not just a few illustrative rows in prose.
- Its scale/context will **align with Question 2's world** (500 schools, Tripura,
  Vidyajyoti/Regular split) so the two answers read as one coherent Labhya simulation.
- The dashboard will be presented as a **visual wireframe/artifact**, not a prose-only
  description.

---

## 5. Open Questions / Ambiguities to Resolve Before Designing the Solution

These are things the prompt does not specify and that the next phase (actual funnel +
dashboard design) will need to make a call on:
- What exact fields/levels constitute "key fields, levels, and relationships" for each
  source (e.g. is the grain of the observation tool one row per visit, or per
  indicator-per-visit?).
- What time lag between training and a "valid" post-training observation should count
  toward assessing practice change.
- How teacher and school identities are expected to reconcile between the two source
  systems (the prompt doesn't state whether they share a common ID scheme).
- What "insight" specifically means for program/state teams — i.e., what decision the
  dashboard is meant to drive (re-training vs coaching vs monitoring gaps), which isn't
  stated explicitly but is implied by "identify where support is needed."

---

## Next Step

Use this document as the shared context/spec when designing: (a) the dummy dataset
schema and generation, (b) the training→practice→insight funnel logic, and (c) the
dashboard UI — as a separate solutioning pass.
