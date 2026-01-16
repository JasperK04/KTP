# Command Line Interface Documentation

## Overview

The Command Line Interface (CLI) provides an interactive frontend for the **Fastener Recommendation Knowledge System**.
It is designed explicitly for **testing, validation, and transparency** during development and expert evaluation.

The CLI is intentionally thin:

* it contains **no domain knowledge**
* it performs **no inference logic**
* it delegates all reasoning to the input model, rule engine, and problem-solving model

This strict separation aligns with Knowledge Technology principles and supports expert-verifiable systems.

---

## Usage

activate the virtual environment
```bash
source .venv/bin/activate
```

then
```bash
python cli_test.py
```

---

## Interaction Model

* Questions are asked sequentially based on applicability conditions.
* Each question can be:

  * answered (boolean or enum choice)
  * skipped using `s`
* After **every answered question**, the system:

  1. updates the domain model
  2. reruns forward-chaining inference
  3. updates candidate recommendations
  4. writes a debug snapshot to `debug_state.yaml`

---

## Incremental Debug State Saving

### Rationale

Inference in a knowledge-based system is incremental and monotonic.
Saving only a final state obscures how conclusions were reached.

The CLI therefore writes debug output after each answered question, exposing the evolving knowledge state.

This supports:

* rule validation
* expert walkthroughs
* debugging unexpected recommendations
* verification & validation requirements

---

## Debug Output Files

### File Naming

Each run of the CLI overwrites the previous YAML file:
`debug_state.yaml`

The file is updated after each question resulting in one continues debug state.
Timestamped questions and the answers are appended while internal states are updated.

---

## Debug State Structure

The debug file has the following schema.

### Top-Level Fields

```yaml
timestamp:               # ISO-8601 timestamp
answers:                 # all answers given so far
derived_requirements:    # inferred constraints from rules
recommendation_count:    # N
question_history:        # chronological audit trail
recommendations:         # current matching fasteners
```

---

### Answers

```yaml
answers:
  material_a_type: wood
  environment_moisture: outdoor
  permanence: permanent
```

This section always reflects the **complete answer state**, not just the most recent input.

---

### Derived Requirements

```yaml
derived_requirements:
  min_tensile_strength: high
  min_water_resistance: good
  allowed_rigidities:
    - rigid
  excluded_categories:
    - adhesive
```

These values result from **forward-chaining rule inference**.
Ordinal properties (e.g. strength, resistance) only increase monotonically.

---

### Question History

```yaml
question_history:
  - question_id: environment_moisture
    question_text: What level of moisture exposure will the joint face?
    answer: outdoor
    timestamp: '2026-01-15T21:03:41.921882'
```

This provides a complete **audit trail**:

* exact question wording
* given answers
* order and timing

---

### Recommendations

```yaml
recommendations:
  - name: Stainless Steel Bolt
    category: mechanical
    tensile_strength: very_high
    shear_strength: high
    rigidity: rigid
    permanence: permanent
```

This section shows the **current filtering result**.
meaning if you check the debug file while not finished, this section shows what fasteners are currently available to you.

---

## Typical Testing Workflow

1. Run the CLI
2. Answer questions interactively
3. Inspect `debug_state.yaml` after each answer
4. Observe how:
   * requirements tighten
   * categories are excluded
   * recommendations disappear

---

## Design Guarantees

* Debug files are **fully rewritten** every time you run the script
* Each `debug_state.yaml` file is **internally consistent**
* CLI behavior is deterministic given identical answers
* Debug output has **no effect on inference behavior**

---

## Intended Audience

This CLI is intended for:

* debugging inference behavior
* validating rule coverage
* expert performing walkthroughs
* evaluating transparency and traceability

It is **not** intended as an end-user interface.
