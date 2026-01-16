# Scenario Testing Guide

## Overview

The test scenarios in `kb_scenarios.py` are organized into 4 focus areas to systematically validate the knowledge base rules:

| Group | Focus Area | Description |
|-------|------------|-------------|
| A | Materials | Material-specific rules (wood, metal, paper, fabric, glass, ceramic) |
| B | Environment | Environmental conditions (moisture, UV, temperature, chemicals) |
| C | Loads | Mechanical constraints (dynamic loads, vibration, shock, tension) |
| D | Edge Cases | Constraint combinations and boundary conditions |

## Running Scenarios

Run all 27 test scenarios:

```bash
uv run python tests/run_scenarios.py
```

This generates results files in `tests/results/`:
- `group_a_results.yaml` - Material scenario results
- `group_b_results.yaml` - Environmental scenario results
- `group_c_results.yaml` - Load scenario results
- `group_d_results.yaml` - Edge case results

## File Structure

```
tests/
├── kb_scenarios.py           # 27 test scenarios
├── run_scenarios.py          # Scenario runner
└── results/                  # Generated results
    ├── group_a_results.yaml
    ├── group_b_results.yaml
    ├── group_c_results.yaml
    └── group_d_results.yaml
```

## Current Status

All 27 scenarios pass:

| Group | Scenarios | Status |
|-------|-----------|--------|
| A | 7 | ✓ All pass |
| B | 7 | ✓ All pass |
| C | 6 | ✓ All pass |
| D | 7 | ✓ All pass |

## Re-running After KB Changes

After modifying `kb.json`, re-run scenarios to verify changes:

```bash
uv run python tests/run_scenarios.py
```

Review any failures in the results files to understand which rules or fasteners need adjustment.
