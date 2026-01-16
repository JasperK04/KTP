# Agent Testing Instructions

## Quick Start for Running Agents in Parallel

### Step 1: Open 4 Composer Windows
Press `Cmd+I` (Mac) or `Ctrl+I` (Windows) four times to create 4 separate Composer sessions.

### Step 2: Assign Each Agent Their Task
Copy-paste the appropriate prompt into each Composer:

---

**Agent A Prompt (Material Scenarios):**
```
You are Agent A reviewing material-specific test scenarios for the fastener recommendation system.

Your task:
1. Read @tests/results/agent_a_results.yaml - these are YOUR assigned scenario results
2. Read @src/kb.json to understand the current knowledge base
3. Analyze why scenarios failed (missing categories, unexpected fasteners)
4. Write your findings to @tests/reports/agent_a_report.md using the template @tests/agent_report_template.md

Focus on: wood, metal, paper, fabric, glass, ceramic material rules.
```

---

**Agent B Prompt (Environmental Scenarios):**
```
You are Agent B reviewing environmental test scenarios for the fastener recommendation system.

Your task:
1. Read @tests/results/agent_b_results.yaml - these are YOUR assigned scenario results
2. Read @src/kb.json to understand the current knowledge base
3. Analyze why scenarios failed (missing categories, unexpected fasteners)
4. Write your findings to @tests/reports/agent_b_report.md using the template @tests/agent_report_template.md

Focus on: moisture, UV, temperature, chemical exposure rules.
```

---

**Agent C Prompt (Load Scenarios):**
```
You are Agent C reviewing load and mechanical test scenarios for the fastener recommendation system.

Your task:
1. Read @tests/results/agent_c_results.yaml - these are YOUR assigned scenario results
2. Read @src/kb.json to understand the current knowledge base
3. Analyze why scenarios failed (missing categories, unexpected fasteners)
4. Write your findings to @tests/reports/agent_c_report.md using the template @tests/agent_report_template.md

Focus on: dynamic loads, vibration, shock, tension, shear strength rules.
```

---

**Agent D Prompt (Edge Cases):**
```
You are Agent D reviewing edge case test scenarios for the fastener recommendation system.

Your task:
1. Read @tests/results/agent_d_results.yaml - these are YOUR assigned scenario results
2. Read @src/kb.json to understand the current knowledge base
3. Analyze why scenarios failed (missing categories, unexpected fasteners)
4. Write your findings to @tests/reports/agent_d_report.md using the template @tests/agent_report_template.md

Focus on: constraint combinations, one-sided access, health restrictions, flexibility requirements.
```

---

### Step 3: Let Agents Work
Each agent will:
- Read their assigned results file
- Analyze the kb.json rules
- Identify issues
- Write their report

### Step 4: Review Reports
Once complete, you'll have 4 report files in `tests/reports/`:
- `agent_a_report.md` - Material analysis
- `agent_b_report.md` - Environmental analysis  
- `agent_c_report.md` - Load analysis
- `agent_d_report.md` - Edge case analysis

---

## File Structure

```
tests/
├── kb_scenarios.py        # 27 test scenarios (read-only)
├── run_scenarios.py       # Scenario runner (run this first)
├── agent_report_template.md  # Template for agent reports
├── README_AGENTS.md       # This file
├── results/               # Generated results (read-only for agents)
│   ├── agent_a_results.yaml
│   ├── agent_b_results.yaml
│   ├── agent_c_results.yaml
│   └── agent_d_results.yaml
└── reports/               # Agent output goes here
    ├── agent_a_report.md
    ├── agent_b_report.md
    ├── agent_c_report.md
    └── agent_d_report.md
```

## Current Test Results Summary

| Agent | Focus | Passed | Failed | Pass Rate |
|-------|-------|--------|--------|-----------|
| A | Materials | 2 | 5 | 28.6% |
| B | Environment | 0 | 7 | 0.0% |
| C | Loads | 1 | 5 | 16.7% |
| D | Edge Cases | 3 | 4 | 42.9% |
| **Total** | | **6** | **21** | **22.2%** |

## Re-running Scenarios

After making changes to `kb.json`, re-run the scenarios:

```bash
uv run python tests/run_scenarios.py
```

This regenerates all results files.
