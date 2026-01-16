# Agent D Review Report: Edge Cases and Constraint Combinations

**Agent ID:** D  
**Review Date:** 2026-01-16  
**Results File:** `tests/results/agent_d_results.yaml`

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Total Scenarios | 7 |
| Passed | 3 |
| Failed | 4 |
| Pass Rate | 42.9% |

**Overall Assessment:** The knowledge base handles basic constraint combinations reasonably well, but fails on several critical edge cases involving one-sided access filtering, health constraint exclusions for toxic adhesives, flexibility requirements conflicting with adhesive exclusions, and overly broad brittle material exclusions. These failures indicate gaps in rule logic and missing health-safety rules.

---

## 2. Scenario Results Analysis

### 2.1 Passing Scenarios

| ID | Name | Notes |
|----|------|-------|
| D04 | Contradictory: Permanent but Removable | Correctly handled removable constraint, excluded permanent adhesives |
| D05 | Everything Excluded Scenario | Correctly identified no valid solutions for extreme constraints |
| D06 | Immediate Curing Constraint | Correctly excluded slow-curing adhesives, recommended mechanical fasteners |

### 2.2 Failing Scenarios

#### Scenario D01: One-Sided Access Panel

**Problem:** System recommended Hex bolt, which requires two-sided access, when only one-sided access is available. Expected Sheet metal screw or rivet instead.

**Root Cause Analysis:**
- Which rules fired: `high_shear_excludes_weak_adhesives`, `immediate_use_required`, `low_porosity_materials`, `metal_to_metal`, `overhead_installation_requires_shear`, `removable_connection`, `static_load`, `vertical_or_overhead`
- Which rules should have fired but didn't: None - rules are correct
- Which rules fired incorrectly: None

**Code Issue Identified:** There is an attribute name mismatch between `kb.json` and the domain model:
- `kb.json` question attribute: `constraints.one_sided_access` (line 192)
- Domain model attribute: `one_side_accessable` (domain_model.py line 303)
- Solving model check: `task.constraints.one_side_accessable` (solving_model.py line 133)

The input model's `_apply_answer` method uses `setattr(target, attr, value)` where `attr` is the last part of the path (`one_sided_access`), but the domain model expects `one_side_accessable`. This mismatch prevents the one-sided access constraint from being properly set, allowing two-sided fasteners to pass through.

**Proposed Fix:** 
1. **Code Fix (High Priority):** Update `kb.json` question attribute from `constraints.one_sided_access` to `constraints.one_side_accessable` to match the domain model, OR update the domain model to use `one_sided_access` consistently.
2. **KB Fix:** Ensure Sheet metal screw and rivet are properly marked as `requires_two_sided_access: false` (they already are in kb.json).

---

#### Scenario D02: Health-Restricted School Project

**Problem:** System recommended Contact cement, which emits toxic fumes and should be excluded for health-constrained scenarios involving children. Expected only Wood glue (PVA) and Staple.

**Root Cause Analysis:**
- Which rules fired: `health_constraints`, `static_load`, `wood_to_wood`
- Which rules should have fired but didn't: A rule to exclude toxic/fume-emitting adhesives when health constraints are present
- Which rules fired incorrectly: None

**Root Cause:** The `health_constraints` rule only excludes the `thermal` category (welding, brazing), but does not exclude toxic adhesives like Contact cement, which emits volatile organic compounds (VOCs) and is unsuitable for children's projects.

**Proposed Fix:** 
1. **Add new rule:** Create a rule that excludes toxic adhesives when health constraints are present. Contact cement, Superglue (cyanoacrylate), and other fume-emitting adhesives should be excluded.
2. **Alternative:** Add a `health_safe` property to fasteners in `kb.json` and filter based on this property when health constraints are present.

---

#### Scenario D03: Flexible Joint Requirement

**Problem:** System returned 0 recommendations when flexible adhesives (Silicone sealant, Contact cement) should have been recommended. Also encountered error: "Unknown question: tension_dominant".

**Root Cause Analysis:**
- Which rules fired: `flexibility_required`, `flexible_implies_low_strength`, `light_dynamic_load`, `low_porosity_materials`, `permanent_connection`
- Which rules should have fired but didn't: None
- Which rules fired incorrectly: The `low_porosity_materials` rule excludes ALL adhesives, but flexible adhesives should still be allowed when flexibility is required

**Root Cause:** There is a rule conflict:
1. `flexibility_required` rule sets `allowed_rigidities: [flexible, semi_flexible]` but does NOT exclude adhesives
2. `low_porosity_materials` rule excludes ALL adhesives when materials have low porosity (plastic has low porosity)
3. `flexible_implies_low_strength` sets `min_tensile_strength: low` and `allowed_rigidities: [flexible, semi_flexible]`

The `low_porosity_materials` rule is too broad - it excludes adhesives entirely, but flexible adhesives (like silicone sealant) can work on low-porosity materials when flexibility is required. The rule should either:
- Not exclude adhesives when flexibility is required, OR
- Only exclude rigid adhesives, not flexible ones

**Additional Issue:** The question ID `tension_dominant` is used in the scenario but the actual question ID in `kb.json` is `load_direction` (line 159). The attribute path is `load.tension_dominant`, but the question ID mismatch causes the error.

**Proposed Fix:**
1. **Modify `low_porosity_materials` rule:** Add condition to NOT exclude adhesives when `flexibility_required` is true, OR change the rule to only exclude rigid adhesives
2. **Fix question ID:** Update scenario to use `load_direction` instead of `tension_dominant`, OR add alias handling in input model

---

#### Scenario D07: Maximum Exclusion Stacking

**Problem:** System returned 0 recommendations when mechanical fasteners (Lag bolt, Concrete screw) should have been recommended for wood-to-masonry connection. Also encountered error: "Unknown question: tension_dominant".

**Root Cause Analysis:**
- Which rules fired: `brittle_materials_present`, `heavy_dynamic_load`, `high_shear_excludes_weak_adhesives`, `masonry_involved`, `no_uv_but_outdoor`, `outdoor_environment`, `overhead_installation_requires_shear`, `permanent_connection`, `vertical_or_overhead`
- Which rules should have fired but didn't: None
- Which rules fired incorrectly: `brittle_materials_present` excludes mechanical fasteners too broadly

**Root Cause:** The `brittle_materials_present` rule excludes mechanical fasteners when ANY material has brittleness "high". In this scenario:
- Wood has brittleness "low"
- Masonry has brittleness "high"

The rule fires and excludes ALL mechanical fasteners, but this is incorrect because:
1. Wood can accept mechanical fasteners (Lag bolt is designed for wood)
2. Masonry can accept mechanical fasteners designed for it (Concrete screw, Masonry nail)
3. The brittleness exclusion should only apply when BOTH materials are brittle, or when the fastener would create point loads on brittle materials

The rule is too conservative - it should allow mechanical fasteners that are compatible with the non-brittle material, or fasteners specifically designed for brittle materials (like concrete screws for masonry).

**Proposed Fix:**
1. **Modify `brittle_materials_present` rule:** Change condition to exclude mechanical only when BOTH materials are brittle, OR
2. **Add exception:** Allow mechanical fasteners that are specifically designed for brittle materials (e.g., Concrete screw, Masonry nail) even when brittle materials are present
3. **Alternative approach:** Make the rule material-pair aware - exclude mechanical only when the fastener would create point loads on brittle materials

---

## 3. Knowledge Base Issues Found

### 3.1 Rule Issues

| Rule ID | Issue | Suggested Fix |
|---------|-------|---------------|
| `low_porosity_materials` | Too broad - excludes all adhesives even when flexibility is required | Add condition to allow flexible adhesives when `flexibility_required` is true |
| `brittle_materials_present` | Too conservative - excludes mechanical when ANY material is brittle | Change to exclude only when BOTH materials are brittle, or add exceptions for masonry/stone-specific fasteners |
| `health_constraints` | Only excludes thermal, missing toxic adhesives | Add exclusion for toxic/fume-emitting adhesives (Contact cement, Superglue, etc.) |

#### Detailed Rule Analysis

**Rule: `low_porosity_materials`**
- Current conditions: `materials.any.porosity: "low"`
- Current effects: `requirements.excluded_categories: ["adhesive"]`
- Problem: Excludes all adhesives when any material has low porosity, but flexible adhesives (silicone, contact cement) can work on low-porosity materials when flexibility is required
- Suggested conditions: `materials.any.porosity: "low"` AND `constraints.flexibility_required: false` (or similar logic)
- Suggested effects: `requirements.excluded_categories: ["adhesive"]` (only for rigid adhesives), OR add exception when flexibility is required

**Rule: `brittle_materials_present`**
- Current conditions: `materials.any.brittleness: "high"`
- Current effects: `requirements.excluded_categories: ["mechanical"]`
- Problem: Excludes mechanical fasteners when ANY material is brittle, but masonry (brittle) can accept masonry-specific mechanical fasteners, and wood-to-masonry connections should allow wood fasteners
- Suggested conditions: `materials.any.brittleness: "high"` AND `materials.both.brittleness: "high"` (only exclude when both are brittle), OR add exception for masonry/stone-specific fasteners
- Suggested effects: Keep same, but with refined conditions

**Rule: `health_constraints`**
- Current conditions: `constraints.health_constraints: true`
- Current effects: `requirements.excluded_categories: ["thermal"]`
- Problem: Only excludes thermal methods, but many adhesives emit toxic fumes (Contact cement, Superglue, etc.) and should be excluded for health-constrained scenarios
- Suggested conditions: Keep same
- Suggested effects: Add exclusion for specific toxic adhesives, OR add new rule for toxic adhesives

### 3.2 Fastener Property Issues

| Fastener | Property | Current Value | Suggested Value | Reasoning |
|----------|----------|---------------|-----------------|-----------|
| Contact cement | (missing) | N/A | `health_safe: false` | Emits toxic VOCs, unsuitable for health-constrained scenarios |
| Superglue (cyanoacrylate) | (missing) | N/A | `health_safe: false` | Emits fumes, can cause skin irritation |
| Silicone sealant | `requires_two_sided_access` | `false` | `false` (correct) | Can be applied one-sided |
| Contact cement | `requires_two_sided_access` | `false` | `false` (correct) | Can be applied one-sided |

**Note:** Consider adding a `health_safe` boolean property to fasteners to enable health constraint filtering.

### 3.3 Missing Rules

| Suggested Rule ID | Context | Conditions | Effects |
|-------------------|---------|------------|---------|
| `health_constraints_exclude_toxic_adhesives` | Exclude toxic/fume-emitting adhesives when health constraints are present | `constraints.health_constraints: true` | Exclude specific adhesives (Contact cement, Superglue) or add to excluded categories with exception logic |
| `flexibility_required_allows_flexible_adhesives` | Allow flexible adhesives even on low-porosity materials when flexibility is required | `constraints.flexibility_required: true` AND `materials.any.porosity: "low"` | Override `low_porosity_materials` exclusion for flexible adhesives |
| `brittle_materials_allow_masonry_fasteners` | Allow masonry-specific mechanical fasteners even when brittle materials are present | `materials.any.material_type: "masonry"` AND `materials.any.brittleness: "high"` | Exception to `brittle_materials_present` for Concrete screw, Masonry nail |

### 3.4 Question Issues

| Question ID | Issue | Suggested Fix |
|-------------|-------|---------------|
| `load_direction` | Scenario uses `tension_dominant` as question ID, but actual ID is `load_direction` | Update scenarios to use `load_direction`, OR add question ID alias handling in input model |
| `access_one_side` | Attribute path `constraints.one_sided_access` doesn't match domain model `one_side_accessable` | Update kb.json attribute to `constraints.one_side_accessable` to match domain model |

---

## 4. Codebase Issues

### 4.1 Input Model Issues

**Attribute Name Mismatch:**
- `kb.json` defines question with attribute `constraints.one_sided_access` (line 192)
- Domain model expects `one_side_accessable` (domain_model.py line 303)
- Input model's `_apply_answer` uses the last part of the path as the attribute name, causing a mismatch
- **Impact:** One-sided access constraint is not properly applied, allowing two-sided fasteners to be recommended

**Question ID Mismatch:**
- Scenarios use `tension_dominant` as question ID
- Actual question ID in `kb.json` is `load_direction` (line 159)
- **Impact:** Causes "Unknown question" errors in scenarios D03, D05, D07

### 4.2 Rule Engine Issues

No issues identified in rule engine logic.

### 4.3 Solving Model Issues

The one-sided access filtering logic is correct (line 133), but the constraint value is not being set due to the attribute name mismatch in the input model.

### 4.4 Other Issues

None identified.

---

## 5. Recommendations

### 5.1 High Priority Changes

Changes that must be made to fix critical issues:

1. **Fix attribute name mismatch for one-sided access:**
   - Update `kb.json` question attribute from `constraints.one_sided_access` to `constraints.one_side_accessable`
   - OR update domain model to use `one_sided_access` consistently
   - **Impact:** Fixes D01 scenario failure

2. **Fix question ID mismatch:**
   - Update scenarios to use `load_direction` instead of `tension_dominant`
   - OR add question ID alias handling in input model
   - **Impact:** Fixes errors in D03, D05, D07

3. **Modify `low_porosity_materials` rule:**
   - Add exception to allow flexible adhesives when `flexibility_required` is true
   - **Impact:** Fixes D03 scenario failure

4. **Add health constraint rule for toxic adhesives:**
   - Create rule to exclude Contact cement, Superglue, and other toxic adhesives when health constraints are present
   - **Impact:** Fixes D02 scenario failure

### 5.2 Medium Priority Changes

Changes that would improve recommendations:

1. **Refine `brittle_materials_present` rule:**
   - Change to exclude mechanical only when BOTH materials are brittle
   - OR add exceptions for masonry/stone-specific fasteners
   - **Impact:** Fixes D07 scenario failure, improves recommendations for wood-to-masonry connections

2. **Add `health_safe` property to fasteners:**
   - Add boolean property to fastener definitions
   - Use in solving model to filter when health constraints are present
   - **Impact:** More maintainable than hardcoding exclusions in rules

### 5.3 Low Priority / Nice-to-Have

Improvements that could be considered:

1. **Add question ID aliases in input model:**
   - Support multiple question IDs mapping to same question
   - **Impact:** More flexible scenario definitions

2. **Improve rule conflict detection:**
   - Add validation to detect when rules create impossible constraints
   - **Impact:** Better debugging and rule maintenance

---

## 6. Proposed kb.json Patches

### Patch 1: Fix One-Sided Access Attribute Name

```json
// Location: questions[13] (access_one_side question)
// Action: modify

{
  "id": "access_one_side",
  "text": "Is only one side of the materials accessible during installation?",
  "attribute": "constraints.one_side_accessable",  // Changed from "constraints.one_sided_access"
  "type": "boolean",
  "helps_rules": []
}
```

### Patch 2: Modify low_porosity_materials Rule to Allow Flexible Adhesives

```json
// Location: rules[2] (low_porosity_materials)
// Action: modify

{
  "id": "low_porosity_materials",
  "context": "Limits adhesive use when materials have low surface porosity, except when flexibility is required.",
  "conditions": {
    "materials.any.porosity": "low",
    "constraints.flexibility_required": false  // Add this condition
  },
  "effects": {
    "requirements.excluded_categories": ["adhesive"]
  }
}
```

**Alternative approach:** Create a new rule that overrides this exclusion:

```json
// Location: rules[] (add new rule)
// Action: add

{
  "id": "flexibility_required_allows_flexible_adhesives",
  "context": "Allows flexible adhesives on low-porosity materials when flexibility is required.",
  "conditions": {
    "constraints.flexibility_required": true,
    "materials.any.porosity": "low"
  },
  "effects": {
    "requirements.allowed_categories": ["adhesive"]  // Override exclusion for flexible adhesives
  }
}
```

### Patch 3: Refine brittle_materials_present Rule

```json
// Location: rules[1] (brittle_materials_present)
// Action: modify

{
  "id": "brittle_materials_present",
  "context": "Avoids mechanical fastening when both materials are brittle, or when fastener would create point loads on brittle materials.",
  "conditions": {
    "materials.both.brittleness": "high"  // Changed from "materials.any.brittleness": "high"
  },
  "effects": {
    "requirements.excluded_categories": ["mechanical"]
  }
}
```

**Alternative approach:** Add exception rule for masonry:

```json
// Location: rules[] (add new rule)
// Action: add

{
  "id": "brittle_materials_allow_masonry_fasteners",
  "context": "Allows masonry-specific mechanical fasteners even when brittle materials are present.",
  "conditions": {
    "materials.any.material_type": "masonry",
    "materials.any.brittleness": "high"
  },
  "effects": {
    "requirements.allowed_categories": ["mechanical"]  // Override exclusion for masonry fasteners
  }
}
```

### Patch 4: Add Health Constraint Rule for Toxic Adhesives

```json
// Location: rules[] (add new rule)
// Action: add

{
  "id": "health_constraints_exclude_toxic_adhesives",
  "context": "Excludes toxic or fume-emitting adhesives when health constraints are present.",
  "conditions": {
    "constraints.health_constraints": true
  },
  "effects": {
    "requirements.excluded_fasteners": ["Contact cement", "Superglue (cyanoacrylate)"]  // Requires new field in requirements
  }
}
```

**Note:** This requires adding `excluded_fasteners` field to requirements, OR adding `health_safe` property to fasteners and filtering in solving model.

**Alternative approach using fastener property:**

```json
// Location: fasteners[] (modify Contact cement and Superglue)
// Action: modify (add health_safe property - requires schema change)

// For Contact cement (fasteners[8]):
{
  "name": "Contact cement",
  "category": "adhesive",
  // ... existing properties ...
  "health_safe": false  // Add this
}

// For Superglue (fasteners[5]):
{
  "name": "Superglue (cyanoacrylate)",
  "category": "adhesive",
  // ... existing properties ...
  "health_safe": false  // Add this
}
```

Then add filtering in solving model's `_fastener_satisfies_requirements` method.

---

## 7. Testing Notes

### Scenario Adjustments Needed:

1. **D03, D05, D07:** Update question ID from `tension_dominant` to `load_direction` in scenario definitions

### Edge Cases to Consider Adding:

1. **One-sided access with flexible requirement:** Test that flexible adhesives work with one-sided access
2. **Health constraints with paper/wood:** Verify non-toxic adhesives are recommended
3. **Brittle + non-brittle material pairs:** Test that appropriate fasteners are allowed (e.g., wood-to-glass with adhesives)

### Expectations Validation:

- D01 expectations are correct: Sheet metal screw and rivet are appropriate for one-sided metal-to-metal
- D02 expectations are correct: Contact cement should be excluded for health constraints
- D03 expectations are correct: Flexible adhesives should be recommended
- D07 expectations are correct: Mechanical fasteners should work for wood-to-masonry

---

## 8. Sign-off

**Reviewed by:** Agent D  
**Confidence Level:** High  
**Requires Follow-up:** Yes

**Follow-up Items:**
1. Verify attribute name fix resolves D01 issue
2. Confirm rule modifications don't break other scenarios
3. Decide on approach for health constraint filtering (rule-based vs. property-based)
4. Test brittle material rule refinement with other material combinations

---

*This report was generated as part of the KB validation process.*
