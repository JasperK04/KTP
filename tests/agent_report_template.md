# Agent Review Report Template

**Agent ID:** [A/B/C/D]  
**Review Date:** [YYYY-MM-DD]  
**Results File:** `tests/results/agent_X_results.yaml`

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Total Scenarios | |
| Passed | |
| Failed | |
| Pass Rate | |

**Overall Assessment:** [Brief 1-2 sentence assessment of KB quality for your assigned domain]

---

## 2. Scenario Results Analysis

### 2.1 Passing Scenarios

List scenarios that passed and any observations:

| ID | Name | Notes |
|----|------|-------|
| | | |

### 2.2 Failing Scenarios

For each failing scenario, analyze the root cause:

#### Scenario [ID]: [Name]

**Problem:** [What went wrong - missing expected results, unexpected results, etc.]

**Root Cause Analysis:**
- Which rules fired: [list from results]
- Which rules should have fired but didn't: [analysis]
- Which rules fired incorrectly: [analysis]

**Proposed Fix:** [Specific kb.json change needed]

---

## 3. Knowledge Base Issues Found

### 3.1 Rule Issues

List any problems with rules in `kb.json`:

| Rule ID | Issue | Suggested Fix |
|---------|-------|---------------|
| | | |

#### Detailed Rule Analysis

For significant rule issues, provide detailed analysis:

**Rule: [rule_id]**
- Current conditions: `{...}`
- Current effects: `{...}`
- Problem: [description]
- Suggested conditions: `{...}`
- Suggested effects: `{...}`

### 3.2 Fastener Property Issues

List any problems with fastener definitions:

| Fastener | Property | Current Value | Suggested Value | Reasoning |
|----------|----------|---------------|-----------------|-----------|
| | | | | |

### 3.3 Missing Rules

Rules that should exist but don't:

| Suggested Rule ID | Context | Conditions | Effects |
|-------------------|---------|------------|---------|
| | | | |

### 3.4 Question Issues

Problems with question definitions or conditional logic:

| Question ID | Issue | Suggested Fix |
|-------------|-------|---------------|
| | | |

---

## 4. Codebase Issues

Report any bugs or problems encountered in the Python code:

### 4.1 Input Model Issues
[Any problems with `src/input_model.py`]

### 4.2 Rule Engine Issues  
[Any problems with `src/rule_model.py`]

### 4.3 Solving Model Issues
[Any problems with `src/solving_model.py`]

### 4.4 Other Issues
[Any other code problems]

---

## 5. Recommendations

### 5.1 High Priority Changes
Changes that must be made to fix critical issues:

1. [Change 1]
2. [Change 2]

### 5.2 Medium Priority Changes
Changes that would improve recommendations:

1. [Change 1]
2. [Change 2]

### 5.3 Low Priority / Nice-to-Have
Improvements that could be considered:

1. [Change 1]
2. [Change 2]

---

## 6. Proposed kb.json Patches

Provide specific JSON patches for recommended changes:

### Patch 1: [Description]

```json
// Location: rules[X] or fasteners[X] or questions[X]
// Action: modify/add/remove

{
  "id": "rule_id",
  "context": "...",
  "conditions": {
    // ...
  },
  "effects": {
    // ...
  }
}
```

### Patch 2: [Description]

```json
// ...
```

---

## 7. Testing Notes

Any observations about the test scenarios themselves:

- Are there scenarios that need adjustment?
- Are there edge cases that should be added?
- Are expectations in scenarios correct?

---

## 8. Sign-off

**Reviewed by:** Agent [A/B/C/D]  
**Confidence Level:** [High/Medium/Low]  
**Requires Follow-up:** [Yes/No]

---

*This report was generated as part of the KB validation process.*
