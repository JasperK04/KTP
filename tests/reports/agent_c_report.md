# Agent C Review Report: Load and Mechanical Scenarios

**Agent ID:** C  
**Review Date:** 2026-01-16  
**Results File:** `tests/results/agent_c_results.yaml`

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Total Scenarios | 6 |
| Passed | 1 |
| Failed | 5 |
| Pass Rate | 16.7% |

**Overall Assessment:** The knowledge base has critical issues with load and mechanical constraint handling. The primary problems are: (1) overly broad exclusion rules that eliminate mechanical fasteners when they should be available, (2) question ID mapping mismatch causing input errors, (3) rules that prefer thermal methods too aggressively, excluding valid mechanical options, and (4) scenarios where exclusions stack up leaving no allowed categories, resulting in zero recommendations.

---

## 2. Scenario Results Analysis

### 2.1 Passing Scenarios

| ID | Name | Notes |
|----|------|-------|
| C04 | Climbing Wall Hold Mounting | Successfully recommended Hex bolt and Lag bolt for high-tension, shock-load scenario. This is the only scenario where mechanical fasteners were properly recommended. |

### 2.2 Failing Scenarios

#### Scenario C01: Industrial Machine Vibration Mount

**Problem:** Missing category: mechanical. Expected both mechanical (Hex bolt, rivet) and thermal (Metal welding), but only got thermal (Metal welding).

**Root Cause Analysis:**
- Rules fired: `heavy_dynamic_load`, `low_porosity_materials`, `metal_to_metal`, `permanent_connection`, `precision_positioning_required`
- `metal_to_metal` rule correctly sets `allowed_categories: [mechanical, thermal]` and `min_tensile_strength: high`
- However, `rigid_and_permanent_prefers_thermal` rule likely fires and overwrites `allowed_categories` to ONLY `[thermal]`, excluding mechanical
- Error: `Unknown question: tension_dominant` - question ID mismatch between scenarios (`tension_dominant`) and KB (`load_direction`)

**Proposed Fix:** 
1. Modify `rigid_and_permanent_prefers_thermal` rule to not override `allowed_categories` if they already include both mechanical and thermal. Instead, it should add preference weighting or only apply when no other categories are allowed.
2. Fix question ID mapping: scenarios should use `load_direction` or KB should accept `tension_dominant` as an alias.

---

#### Scenario C02: Automotive Impact Bumper

**Problem:** Missing category: mechanical. Expected mechanical (Sheet metal screw, rivet), but got only thermal (Metal welding). This is wrong because plastic-to-metal cannot be welded.

**Root Cause Analysis:**
- Rules fired: `heavy_dynamic_load`, `low_porosity_materials`, `metal_to_metal`, `no_uv_but_outdoor`, `outdoor_environment`
- Critical issue: `metal_to_metal` rule fires because it checks `materials.same_material: true` AND `materials.material_a.material_type: metal`, but material_b is plastic, not metal. However, the rule seems to be incorrectly triggered.
- Actually, looking closer: `metal_to_metal` should NOT fire here (plastic-to-metal), but the system allowed thermal category which only works for metal-to-metal. This suggests the filtering logic allows Metal welding even though materials don't match.
- `vibration_present` and `shock_loads_present` correctly exclude adhesive
- Error: `Unknown question: tension_dominant` - same question ID issue

**Proposed Fix:**
1. Fastener filtering must enforce `compatible_materials` strictly. Metal welding requires BOTH materials to be metal. The solver should reject it for plastic-to-metal joints.
2. Add rule that explicitly allows mechanical category when vibration/shock exclude adhesive for mixed-material joints.
3. Fix question ID mapping issue.

---

#### Scenario C03: Decorative Wall Picture

**Problem:** Missing ALL recommendations (0 results). Expected mechanical (Common nail, Masonry nail).

**Root Cause Analysis:**
- Rules fired: `brittle_materials_present`, `high_shear_excludes_weak_adhesives`, `immediate_use_required`, `masonry_involved`, `overhead_installation_requires_shear`, `removable_connection`, `static_load`, `vertical_or_overhead`
- **Critical issue**: `brittle_materials_present` rule excludes mechanical category when `materials.any.brittleness: high`. Masonry has `brittleness: high`, so mechanical is incorrectly excluded.
- `vertical_or_overhead` excludes adhesive (correct)
- `immediate_use_required` excludes adhesive (correct)
- `removable_connection` excludes thermal (correct)
- Result: ALL categories excluded (adhesive, mechanical, thermal) → 0 recommendations

**Proposed Fix:**
1. `brittle_materials_present` rule is too broad. Masonry IS brittle but mechanical fasteners designed for masonry (Masonry nail, Concrete screw) work correctly. The rule should either:
   - Only exclude mechanical when brittleness is `very_high` (glass, ceramic), OR
   - Have an exception for masonry/stone materials, OR
   - Be more specific about which mechanical fasteners are excluded (e.g., point-load fasteners for glass, but masonry-compatible fasteners are OK)

---

#### Scenario C05: Overhead Ceiling Light Fixture

**Problem:** Missing ALL recommendations (0 results). Expected mechanical (Concrete screw, Masonry nail).

**Root Cause Analysis:**
- Rules fired: `brittle_materials_present`, `high_shear_excludes_weak_adhesives`, `immediate_use_required`, `masonry_involved`, `overhead_installation_requires_shear`, `permanent_connection`, `precision_positioning_required`, `static_load`, `vertical_or_overhead`
- **Same critical issue as C03**: `brittle_materials_present` excludes mechanical because masonry has `brittleness: high`
- `vertical_or_overhead` excludes adhesive (correct)
- `immediate_use_required` excludes adhesive (correct)
- `permanent_connection` allows permanent (correct, but thermal excluded by other factors)
- Result: ALL categories excluded → 0 recommendations

**Proposed Fix:**
Same as C03: Modify `brittle_materials_present` rule to not exclude mechanical for masonry/stone materials when masonry-compatible mechanical fasteners exist.

---

#### Scenario C06: Precision Optical Instrument Mount

**Problem:** Missing categories: mechanical, adhesive. Expected all three (mechanical: Dowel pin, thermal: Metal welding, adhesive: Two-component epoxy, Metal epoxy), but got only thermal (Metal welding).

**Root Cause Analysis:**
- Rules fired: `low_porosity_materials`, `metal_to_metal`, `permanent_connection`, `precision_positioning_required`, `static_load`
- `metal_to_metal` correctly sets `allowed_categories: [mechanical, thermal]`
- `low_porosity_materials` excludes adhesive (this is correct for metal-to-metal, but high-quality epoxies work on prepared metal surfaces)
- **Issue**: `rigid_and_permanent_prefers_thermal` may be firing again, restricting to thermal only
- **Issue**: Even if mechanical is allowed, Dowel pin requires `requires_two_sided_access: true` but scenario has `access_one_side: false`, which should allow it. However, the rule logic may be excluding it.

**Proposed Fix:**
1. Modify `rigid_and_permanent_prefers_thermal` to not override existing allowed categories when multiple valid options exist.
2. Review `low_porosity_materials` rule: While it correctly excludes most adhesives, high-performance epoxies (Two-component epoxy, Metal epoxy) DO work on low-porosity metals with proper surface preparation. Consider either:
   - Not excluding adhesive category, but instead filtering individual adhesive fasteners by compatibility, OR
   - Adding an exception rule for high-strength epoxies on metal when precision is required
3. Ensure fastener filtering correctly handles `requires_two_sided_access` constraint.

---

## 3. Knowledge Base Issues Found

### 3.1 Rule Issues

| Rule ID | Issue | Suggested Fix |
|---------|-------|---------------|
| `brittle_materials_present` | Too broad - excludes ALL mechanical fasteners when ANY material has `brittleness: high`. Masonry is brittle but masonry-compatible mechanical fasteners (Masonry nail, Concrete screw) work correctly. | Change condition to `brittleness: very_high` OR add exception for masonry/stone materials with compatible fasteners. |
| `rigid_and_permanent_prefers_thermal` | Overly restrictive - when it fires, it sets `allowed_categories` to ONLY `[thermal]`, excluding mechanical options that should also be available. | Only apply this rule when no other categories are explicitly allowed, or use a weighting/preference system instead of hard exclusion. |
| `low_porosity_materials` | Excludes ALL adhesives for low-porosity materials, but high-performance epoxies (Two-component epoxy, Metal epoxy) work on metals with surface preparation. | Either remove this exclusion and rely on fastener `compatible_materials` filtering, OR add exception for high-strength epoxies. |
| `metal_to_metal` | Works correctly but can be overridden by `rigid_and_permanent_prefers_thermal`. Need better rule priority/precedence handling. | Ensure rules that set `allowed_categories` are not easily overridden by preference rules. |

#### Detailed Rule Analysis

**Rule: brittle_materials_present**
- Current conditions: `materials.any.brittleness: high`
- Current effects: `excluded_categories: [mechanical]`
- Problem: Excludes mechanical fasteners for masonry (brittleness: high) when masonry-specific mechanical fasteners (Masonry nail, Concrete screw) are designed to work safely with brittle masonry.
- Suggested conditions: `materials.any.brittleness: very_high` OR `(materials.any.brittleness: high AND NOT materials.any.material_type IN [masonry, stone])`
- Suggested effects: Keep same, but apply more selectively.

---

**Rule: rigid_and_permanent_prefers_thermal**
- Current conditions: `materials.same_material: true`, `materials.material_a.material_type IN [metal, plastic]`, `requirements.allowed_rigidities: rigid`, `constraints.permanence: permanent`
- Current effects: `allowed_categories: [thermal]`
- Problem: This OVERWRITES existing `allowed_categories` rather than adding a preference. When `metal_to_metal` sets `allowed_categories: [mechanical, thermal]`, this rule should not eliminate mechanical.
- Suggested conditions: Same, but add condition: `NOT (requirements.allowed_categories CONTAINS [mechanical])` OR make it only apply when categories are empty.
- Suggested effects: Either use `preferred_categories: [thermal]` instead of `allowed_categories`, OR only apply when `allowed_categories` is empty.

---

### 3.2 Fastener Property Issues

| Fastener | Property | Current Value | Suggested Value | Reasoning |
|----------|----------|---------------|-----------------|-----------|
| Metal welding | compatible_materials | `[metal]` | Keep | Correct - but filtering must enforce this strictly. Metal welding should NEVER be recommended for plastic-to-metal joints (C02). |
| Dowel pin | requires_two_sided_access | `true` | Keep | Correct - but filtering logic must correctly interpret `access_one_side: false` as allowing two-sided access. |

**Issue Found**: The fastener filtering logic may not be correctly enforcing `compatible_materials` constraints. Metal welding was recommended in C02 (plastic-to-metal) when it should have been filtered out.

---

### 3.3 Missing Rules

| Suggested Rule ID | Context | Conditions | Effects |
|-------------------|---------|------------|---------|
| `vibration_excludes_adhesive_allow_mechanical` | When vibration excludes adhesive, explicitly allow mechanical (if not otherwise excluded) | `load.vibration: true` AND `requirements.excluded_categories CONTAINS adhesive` | `allowed_categories: ADD mechanical` (if not excluded) |
| `vertical_excludes_adhesive_allow_mechanical` | Similar for vertical orientation | `constraints.orientation_vertical: true` AND `requirements.excluded_categories CONTAINS adhesive` | `allowed_categories: ADD mechanical` (if not excluded) |
| `masonry_allows_masonry_mechanical` | Explicitly allow mechanical for masonry even if brittle | `materials.any.material_type: masonry` AND `brittle_materials_present` fired | `allowed_categories: ADD mechanical`, with note to prefer masonry-compatible fasteners |

---

### 3.4 Question Issues

| Question ID | Issue | Suggested Fix |
|-------------|-------|---------------|
| `load_direction` | Scenarios use question ID `tension_dominant`, but KB defines it as `load_direction`. Attribute is correctly `load.tension_dominant`. | Either: (1) Change KB question ID to `tension_dominant`, OR (2) Update scenarios to use `load_direction`. Option 1 is better as it matches the attribute name more directly. |

---

## 4. Codebase Issues

### 4.1 Input Model Issues
The input model appears to accept `tension_dominant` as a question answer key, but the KB defines the question ID as `load_direction`. This mismatch causes the "Unknown question: tension_dominant" error in scenarios C01, C02, C04.

**Investigation needed:** Check `src/input_model.py` to see how question IDs are mapped to attribute paths and whether aliasing is supported.

---

### 4.2 Rule Engine Issues
The rule engine may not be handling rule precedence correctly. Rules that set `allowed_categories` are being overridden by preference rules like `rigid_and_permanent_prefers_thermal`. 

**Issue:** When multiple rules affect `allowed_categories`, the last one to fire may overwrite previous values instead of merging them (e.g., intersection for restrictions, union for allowances).

---

### 4.3 Solving Model Issues
The solving model (fastener filtering) appears to not be strictly enforcing `compatible_materials` constraints. In C02, Metal welding was recommended for a plastic-to-metal joint, which should be impossible since Metal welding's `compatible_materials: [metal]` requires both materials to be metal.

**Investigation needed:** Check `src/solving_model.py` to verify that fastener `compatible_materials` is checked against BOTH material_a and material_b types.

---

### 4.4 Other Issues
**Category Exclusion Stacking:** When multiple rules exclude different categories, and no rules explicitly allow categories, the system ends up with empty `allowed_categories`. This causes zero recommendations (C03, C05). 

The system needs either:
1. Default category allowance (e.g., allow all categories initially, then exclude based on rules), OR
2. Explicit allowance rules that fire when exclusions occur (see Missing Rules section), OR
3. Better rule precedence: exclusions should narrow allowed categories, not eliminate them unless all are excluded.

---

## 5. Recommendations

### 5.1 High Priority Changes

1. **Fix `brittle_materials_present` rule**: Change condition to `brittleness: very_high` OR add exception for masonry/stone. This is blocking valid mechanical recommendations in C03 and C05.

2. **Fix question ID mapping**: Change `load_direction` question ID to `tension_dominant` in KB to match scenario expectations, or add alias support in input model.

3. **Fix `rigid_and_permanent_prefers_thermal` rule**: Modify to not override existing `allowed_categories` when mechanical is already allowed. Use preference weighting instead of hard category restriction.

4. **Enforce `compatible_materials` filtering**: Fix solver to strictly check fastener material compatibility. Metal welding should NEVER appear for plastic-to-metal joints (C02).

5. **Fix category exclusion stacking**: Implement default category allowance OR explicit allowance rules when exclusions occur. Prevent empty `allowed_categories` unless truly no options exist.

---

### 5.2 Medium Priority Changes

1. **Review `low_porosity_materials` rule**: Consider allowing high-performance epoxies for metal-to-metal joints when precision is required (C06).

2. **Add explicit mechanical allowance rules**: Create rules that explicitly allow mechanical category when vibration/vertical/shock exclude adhesive, if mechanical isn't otherwise excluded.

3. **Improve rule precedence system**: Ensure rules that allow categories (e.g., `metal_to_metal`) are not easily overridden by preference rules. Consider rule priority or merging logic.

---

### 5.3 Low Priority / Nice-to-Have

1. **Add masonry-specific mechanical fastener preference**: Create rule that prefers masonry-compatible mechanical fasteners when masonry is involved.

2. **Enhance rule logging**: Add better debugging output showing which rules fired and why categories were excluded/allowed.

3. **Add fastener compatibility validation**: Verify that all fasteners with `compatible_materials` constraints can actually be used with the specified material combinations.

---

## 6. Proposed kb.json Patches

### Patch 1: Fix brittle_materials_present rule

```json
// Location: rules[1] (brittle_materials_present)
// Action: modify condition to be more selective

{
  "id": "brittle_materials_present",
  "context": "Avoids mechanical fastening when one or more materials are very brittle (glass, ceramic), but allows masonry-compatible fasteners for masonry.",
  "conditions": {
    "materials.any.brittleness": "very_high"
  },
  "effects": {
    "requirements.excluded_categories": [
      "mechanical"
    ]
  }
}
```

**Alternative approach** - Keep high but add exception rule:

```json
// Location: rules[] (add new rule after brittle_materials_present)
// Action: add new rule

{
  "id": "masonry_allows_mechanical_despite_brittle",
  "context": "Masonry is brittle but masonry-compatible mechanical fasteners work correctly.",
  "conditions": {
    "materials.any.material_type": "masonry",
    "materials.any.brittleness": "high"
  },
  "effects": {
    "requirements.allowed_categories": [
      "mechanical"
    ]
  }
}
```

---

### Patch 2: Fix rigid_and_permanent_prefers_thermal rule

```json
// Location: rules[] (find rigid_and_permanent_prefers_thermal)
// Action: modify to not override existing allowed_categories

{
  "id": "rigid_and_permanent_prefers_thermal",
  "context": "Prefers thermal joining for rigid, permanent joints of identical materials, but only when no other categories are already explicitly allowed.",
  "conditions": {
    "materials.same_material": true,
    "materials.material_a.material_type": [
      "metal",
      "plastic"
    ],
    "requirements.allowed_rigidities": "rigid",
    "constraints.permanence": "permanent",
    "NOT": {
      "requirements.allowed_categories": {
        "contains": "mechanical"
      }
    }
  },
  "effects": {
    "requirements.allowed_categories": [
      "thermal"
    ]
  }
}
```

**Note:** The `NOT` condition syntax may need to be implemented in the rule engine. If not supported, alternative is to change effects to use preference instead of hard category setting.

---

### Patch 3: Fix question ID for tension_dominant

```json
// Location: questions[] (find load_direction question)
// Action: change id from "load_direction" to "tension_dominant"

{
  "id": "tension_dominant",
  "text": "Is the load primarily pulling (tension) rather than pressing (compression)?",
  "attribute": "load.tension_dominant",
  "type": "boolean",
  "ask_if": {
    "load.load_type": [
      "light_dynamic",
      "heavy_dynamic"
    ]
  },
  "helps_rules": [
    "tension_dominant_load"
  ]
}
```

---

### Patch 4: Add rule to explicitly allow mechanical when adhesive excluded by vibration

```json
// Location: rules[] (add after vibration_present rule)
// Action: add new rule

{
  "id": "vibration_allow_mechanical_when_adhesive_excluded",
  "context": "When vibration excludes adhesive, explicitly allow mechanical fasteners if not otherwise excluded.",
  "conditions": {
    "load.vibration": true,
    "requirements.excluded_categories": {
      "contains": "adhesive"
    },
    "NOT": {
      "requirements.excluded_categories": {
        "contains": "mechanical"
      }
    }
  },
  "effects": {
    "requirements.allowed_categories": [
      "mechanical"
    ]
  }
}
```

**Similar rules needed for:** `vertical_or_overhead` and `shock_loads_present` excluding adhesive.

---

## 7. Testing Notes

1. **Scenario C03 and C05**: These scenarios correctly expect masonry-compatible mechanical fasteners. The test expectations are valid - the KB rule is the problem.

2. **Scenario C02**: The expectation of mechanical (Sheet metal screw, rivet) for plastic-to-metal is correct. Metal welding should never be recommended here.

3. **Scenario C01**: The expectation of both mechanical and thermal is correct. Preference rules should not eliminate valid options.

4. **Scenario C06**: The expectation of all three categories (mechanical, thermal, adhesive) may be optimistic if `low_porosity_materials` rule is intended to exclude adhesives. However, high-performance metal epoxies DO work on metals, so this may be a valid expectation.

5. **Edge case consideration**: What should happen when ALL categories are legitimately excluded? Should the system return an empty result set with explanation, or provide a "least bad" option? Current behavior (empty results) may be acceptable, but requires better user messaging.

---

## 8. Sign-off

**Reviewed by:** Agent C  
**Confidence Level:** High  
**Requires Follow-up:** Yes

**Follow-up Notes:**
- Verify rule engine precedence and merging logic for `allowed_categories`
- Test fastener filtering to ensure `compatible_materials` is strictly enforced
- Confirm question ID mapping behavior in input model
- Consider implementing rule priority system to handle conflicting rules better

---

*This report was generated as part of the KB validation process.*
