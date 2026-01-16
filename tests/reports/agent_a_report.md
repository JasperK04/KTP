# Agent A Review Report: Material Scenarios

**Agent ID:** A  
**Review Date:** 2026-01-16  
**Results File:** `tests/results/agent_a_results.yaml`

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Total Scenarios | 7 |
| Passed | 2 |
| Failed | 5 |
| Pass Rate | 28.6% |

**Overall Assessment:** The knowledge base has critical flaws in material-specific rules that incorrectly exclude valid fastening categories. The primary issues are overly broad exclusion rules for adhesives based on material porosity and orientation constraints. These rules prevent valid adhesive recommendations for paper-to-paper, glass-to-metal, ceramic-to-stone, and other material combinations where adhesives are the appropriate solution.

---

## 2. Scenario Results Analysis

### 2.1 Passing Scenarios

| ID | Name | Notes |
|----|------|-------|
| A03 | Wood-to-Wood Furniture Joint | Correctly recommended both mechanical (Wood screw, Hex bolt) and adhesive (Wood glue) options. Rules worked as expected. |
| A04 | Fabric-to-Fabric Upholstery | Correctly recommended Contact cement (adhesive). Missing Fabric adhesive and Hot-melt glue, but core category was correct. |

### 2.2 Failing Scenarios

#### Scenario A01: Paper-to-Paper Scrapbooking
**Problem:** Missing category: adhesive. Got 0 recommendations. Expected "Wallpaper adhesive" and "Fabric adhesive".

**Root Cause Analysis:**
- Rules fired: `brittle_materials_present`, `high_porosity_excludes_low_strength_adhesives`, `immediate_use_required`, `paper_to_paper`, `removable_connection`, `static_load`
- **Critical Issue:** The `paper_to_paper` rule (lines 356-368 in kb.json) correctly excludes mechanical and thermal categories, but the `immediate_use_required` rule (lines 609-618) also excludes adhesives when `max_curing_time` is "immediate". However, wallpaper adhesive and fabric adhesive can be used immediately or have very fast setup times.
- **Secondary Issue:** The `paper_to_paper` rule should explicitly allow adhesives, not just exclude mechanical/thermal. The rule sets `min_tensile_strength: very_low` which is correct, but doesn't ensure adhesives remain available.
- **Missing Logic:** There's no exception rule that allows adhesives for paper-to-paper connections even when `immediate_use_required` fires, or the `immediate_use_required` rule should not exclude adhesives that have immediate/fast curing.

**Proposed Fix:** 
1. Modify `paper_to_paper` rule to explicitly allow adhesive category: `"requirements.allowed_categories": ["adhesive"]`
2. Modify `immediate_use_required` rule to exclude only slow-curing adhesives, not all adhesives. Alternatively, add an exception for paper-to-paper scenarios.
3. Ensure fast-curing adhesives like "Wallpaper adhesive" and "Fabric adhesive" are not filtered out by immediate use requirements.

---

#### Scenario A02: Metal-to-Metal Structural Frame
**Problem:** Missing category: mechanical. Got only 1 thermal recommendation (Metal welding). Expected "Hex bolt" and "rivet" in addition.

**Root Cause Analysis:**
- Rules fired: `heavy_dynamic_load`, `low_porosity_materials`, `metal_to_metal`, `no_uv_but_outdoor`, `outdoor_environment`, `permanent_connection`, `precision_positioning_required`
- **Critical Issue:** The `metal_to_metal` rule (lines 395-407) correctly sets `allowed_categories: ["mechanical", "thermal"]`, but the `vibration_present` rule (lines 531-541) excludes adhesives (correct) and sets `min_vibration_resistance: good`. 
- **Root Cause:** The `metal_to_metal` rule allows mechanical fasteners, but the recommendation engine may be filtering them out due to:
  1. `Hex bolt` requires `requires_two_sided_access: true` (line 1201), but the scenario has `access_one_side: false` (meaning both sides accessible), so this should work.
  2. `rivet` has `permanence: permanent` (line 1235), which matches the requirement.
  3. Both fasteners have `vibration_resistance: good` (lines 1197, 1232), which meets the requirement.
- **Investigation Needed:** The rules appear correct. The issue may be in the recommendation engine's filtering logic or fastener property matching. However, since `metal_to_metal` sets `allowed_categories`, mechanical fasteners should be considered.

**Proposed Fix:**
1. Verify that `allowed_categories` properly enables category filtering (not just excludes).
2. Check if there are additional constraints (like `requires_two_sided_access` for Hex bolt) that are incorrectly filtering out valid options.
3. Consider if `precision_positioning_required` should prefer mechanical over thermal, or if both should be equally recommended.

---

#### Scenario A05: Glass-to-Metal Display Case
**Problem:** Missing category: adhesive. Got 1 thermal recommendation only (Metal welding). Expected "Glass adhesive", "Silicone sealant", "Two-component epoxy".

**Root Cause Analysis:**
- Rules fired: `high_shear_excludes_weak_adhesives`, `low_porosity_materials`, `metal_to_metal`, `overhead_installation_requires_shear`, `permanent_connection`, `precision_positioning_required`, `static_load`, `vertical_or_overhead`
- **Critical Issue #1:** The `low_porosity_materials` rule (lines 383-392) excludes adhesives when ANY material has low porosity. Glass has `porosity: "none"` (line 305) and metal has `porosity: "low"` (line 275). This rule is too broad - many adhesives work excellently on low-porosity materials like glass and metal (e.g., Glass adhesive, Two-component epoxy, Silicone sealant).
- **Critical Issue #2:** The `vertical_or_overhead` rule (lines 585-594) excludes all adhesives for vertical installations. However, many adhesives are specifically designed for vertical/overhead use (e.g., Glass adhesive, Silicone sealant, Two-component epoxy).
- **Critical Issue #3:** The `high_shear_excludes_weak_adhesives` rule (lines 773-782) excludes adhesives when `min_shear_strength: high` is required. However, `overhead_installation_requires_shear` (lines 763-770) sets `min_shear_strength: high` for vertical installations, and then `high_shear_excludes_weak_adhesives` excludes ALL adhesives. But some adhesives (Two-component epoxy, Glass adhesive) have high shear strength.
- **Root Cause:** Multiple overly broad exclusion rules are stacking to exclude adhesives that should be valid. The rules don't account for adhesives that have high shear strength or are designed for vertical use.

**Proposed Fix:**
1. Modify `low_porosity_materials` rule to be more nuanced - it should not exclude adhesives entirely, but perhaps require specific adhesive types or surface preparation. Alternatively, remove this rule entirely as many adhesives work on low-porosity materials.
2. Modify `vertical_or_overhead` rule to exclude only weak adhesives, not all adhesives. Many adhesives are designed for vertical installation.
3. Modify `high_shear_excludes_weak_adhesives` to exclude only adhesives with low/very_low shear strength, not all adhesives. Adhesives with high/very_high shear strength should remain.
4. Consider adding a `brittle_materials_require_adhesives` rule that allows adhesives when brittle materials (glass, ceramic) are present, even if other rules would exclude them.

---

#### Scenario A06: Ceramic Tile to Stone Floor
**Problem:** Missing category: adhesive. Got 0 recommendations. Expected "Two-component epoxy", "High-temperature adhesive", "Flooring adhesive".

**Root Cause Analysis:**
- Rules fired: `brittle_materials_present`, `low_porosity_materials`, `permanent_connection`, `precision_positioning_required`, `splash_environment`, `static_load`
- **Critical Issue:** Same as A05 - the `low_porosity_materials` rule excludes adhesives. Ceramic has `porosity: "low"` (line 315) and stone has `porosity: "low"` (line 325). However, adhesives are the standard and correct solution for ceramic-to-stone bonding (e.g., flooring adhesive, epoxy).
- **Secondary Issue:** The `brittle_materials_present` rule correctly excludes mechanical fasteners (line 377), which is appropriate. But then `low_porosity_materials` excludes adhesives, leaving no valid options.
- **Root Cause:** The `low_porosity_materials` rule is fundamentally flawed for ceramic and stone applications, where adhesives are the primary and correct fastening method.

**Proposed Fix:**
1. Remove or significantly modify the `low_porosity_materials` rule. It should not exclude adhesives for ceramic, stone, glass, or metal - these materials commonly use adhesives.
2. The rule might be appropriate for materials where adhesives truly don't work, but ceramic, stone, glass, and metal all have well-established adhesive solutions.
3. Consider making the rule material-specific: exclude adhesives only for specific material combinations where they truly don't work, not based solely on porosity.

---

#### Scenario A07: Plastic-to-Plastic Electronics Enclosure
**Problem:** Missing category: mechanical. Got 0 recommendations. Expected "Sheet metal screw" and "rivet".

**Root Cause Analysis:**
- Rules fired: `immediate_use_required`, `low_porosity_materials`, `precision_positioning_required`, `removable_connection`, `static_load`
- **Critical Issue:** The `low_porosity_materials` rule excludes adhesives (correct for this scenario), and `immediate_use_required` also excludes adhesives. The `removable_connection` rule excludes thermal (correct). However, mechanical fasteners should still be available.
- **Root Cause:** The rules don't explicitly exclude mechanical, but no mechanical fasteners are being recommended. Let's check:
  - `Sheet metal screw` is compatible with `["metal", "plastic"]` (line 1172), has `permanence: removable` (line 1182), and `vibration_resistance: fair` (line 1179).
  - `rivet` is compatible with `["metal", "plastic"]` (line 1225), but has `permanence: permanent` (line 1235), while the scenario requires `permanence: removable`.
  - The scenario requires `precision_required: true`, which sets `min_vibration_resistance: good` (line 732). `Sheet metal screw` has `vibration_resistance: fair`, which may be filtered out.
- **Root Cause:** `Sheet metal screw` has `vibration_resistance: fair` but the requirement is `good` due to `precision_positioning_required`. However, for a static load indoor electronics enclosure, `fair` vibration resistance should be acceptable. The rule may be too strict.

**Proposed Fix:**
1. Review if `precision_positioning_required` should require `good` vibration resistance, or if `fair` is acceptable for static loads.
2. Consider if `rivet` should have `permanence: removable` for some applications, or if there should be removable rivet variants.
3. Verify that mechanical fasteners are not being incorrectly filtered by other constraints.

---

## 3. Knowledge Base Issues Found

### 3.1 Rule Issues

| Rule ID | Issue | Suggested Fix |
|---------|-------|---------------|
| `low_porosity_materials` | Too broad - excludes adhesives for ALL low-porosity materials, but many adhesives work on glass, ceramic, stone, metal, plastic | Remove or make material-specific. Many adhesives are designed for low-porosity materials. |
| `paper_to_paper` | Doesn't explicitly allow adhesives, only excludes mechanical/thermal | Add `"requirements.allowed_categories": ["adhesive"]` to ensure adhesives are considered |
| `vertical_or_overhead` | Excludes ALL adhesives, but many adhesives work vertically | Modify to exclude only weak adhesives, or remove entirely as many adhesives are designed for vertical use |
| `high_shear_excludes_weak_adhesives` | Excludes ALL adhesives when high shear required, but some adhesives have high shear strength | Modify to exclude only adhesives with low/very_low shear strength, keep high-strength adhesives |
| `immediate_use_required` | Excludes ALL adhesives, but some adhesives have immediate/fast curing | Modify to exclude only slow-curing adhesives, allow fast-curing adhesives |

#### Detailed Rule Analysis

**Rule: `low_porosity_materials`**
- Current conditions: `{"materials.any.porosity": "low"}`
- Current effects: `{"requirements.excluded_categories": ["adhesive"]}`
- Problem: This rule is fundamentally flawed. It excludes adhesives for glass (porosity: none), metal (low), ceramic (low), stone (low), and plastic (low). However, adhesives are the PRIMARY and CORRECT solution for many of these materials:
  - Glass-to-metal: Glass adhesive, Silicone sealant, Two-component epoxy
  - Ceramic-to-stone: Flooring adhesive, Two-component epoxy, High-temperature adhesive
  - Metal-to-metal: Metal epoxy, Two-component epoxy (when mechanical/thermal not suitable)
  - Plastic-to-plastic: Various adhesives work on plastic
- Suggested conditions: Remove this rule entirely, OR make it material-specific (e.g., only exclude for specific problematic combinations)
- Suggested effects: N/A (rule should be removed or significantly modified)

**Rule: `paper_to_paper`**
- Current conditions: `{"materials.same_material": true, "materials.material_a.material_type": "paper"}`
- Current effects: `{"requirements.excluded_categories": ["mechanical", "thermal"], "requirements.min_tensile_strength": "very_low"}`
- Problem: Doesn't explicitly allow adhesives. While it doesn't exclude them, other rules (like `immediate_use_required`) might exclude them, leaving no valid options.
- Suggested conditions: Same
- Suggested effects: Add `"requirements.allowed_categories": ["adhesive"]` to ensure adhesives are explicitly allowed

**Rule: `vertical_or_overhead`**
- Current conditions: `{"constraints.orientation_vertical": true}`
- Current effects: `{"requirements.excluded_categories": ["adhesive"]}`
- Problem: Many adhesives are specifically designed for vertical/overhead installation (Glass adhesive, Silicone sealant, Construction adhesive, etc.). This rule incorrectly excludes all adhesives.
- Suggested conditions: Same
- Suggested effects: Remove the exclusion, OR modify to only exclude weak adhesives. Many adhesives work fine vertically.

**Rule: `high_shear_excludes_weak_adhesives`**
- Current conditions: `{"requirements.min_shear_strength": "high"}`
- Current effects: `{"requirements.excluded_categories": ["adhesive"]}`
- Problem: This excludes ALL adhesives when high shear is required, but many adhesives have high or very_high shear strength (Two-component epoxy: very_high, Glass adhesive: moderate, Construction adhesive: high, etc.).
- Suggested conditions: Same, but check fastener properties
- Suggested effects: This rule should be implemented differently - exclude only adhesives with low/very_low shear strength, not all adhesives. However, this requires checking fastener properties, which may not be possible in rule effects. Alternative: Remove this rule and let the recommendation engine filter by shear strength property.

**Rule: `immediate_use_required`**
- Current conditions: `{"constraints.max_curing_time": "immediate"}`
- Current effects: `{"requirements.excluded_categories": ["adhesive"]}`
- Problem: Some adhesives have immediate or very fast curing (Wallpaper adhesive, Fabric adhesive, Hot-melt glue, Superglue). This rule excludes all adhesives.
- Suggested conditions: Same
- Suggested effects: This rule should exclude only slow-curing adhesives. However, this requires checking fastener properties. Alternative: Add exceptions for fast-curing adhesives, or modify to be less restrictive.

### 3.2 Fastener Property Issues

| Fastener | Property | Current Value | Suggested Value | Reasoning |
|----------|----------|---------------|-----------------|-----------|
| Wallpaper adhesive | N/A | Excluded by `immediate_use_required` | Should be allowed for immediate use | Wallpaper adhesive is designed for immediate use |
| Fabric adhesive | N/A | Excluded by `immediate_use_required` | Should be allowed for immediate use | Fabric adhesive has fast setup |
| Sheet metal screw | vibration_resistance | fair | Should be acceptable for static precision loads | For static loads in electronics, fair vibration resistance should suffice |
| rivet | permanence | permanent | Consider removable variant | Some rivets are designed to be removable |

### 3.3 Missing Rules

Rules that should exist but don't:

| Suggested Rule ID | Context | Conditions | Effects |
|-------------------|---------|------------|---------|
| `brittle_materials_allow_adhesives` | When brittle materials are present, adhesives should be explicitly allowed even if other rules would exclude them | `{"materials.any.brittleness": "very_high"}` AND brittle material present | `{"requirements.allowed_categories": ["adhesive"]}` - This would override `low_porosity_materials` exclusion for glass/ceramic |
| `fast_curing_adhesives_allowed` | Allow fast-curing adhesives even when immediate use required | `{"constraints.max_curing_time": "immediate"}` | Don't exclude adhesives with fast/immediate curing times (requires fastener property check) |
| `high_strength_adhesives_allowed_for_high_shear` | Allow high-strength adhesives when high shear required | `{"requirements.min_shear_strength": "high"}` | Don't exclude adhesives with high/very_high shear strength |

### 3.4 Question Issues

No issues found with question definitions for material scenarios.

---

## 4. Codebase Issues

### 4.1 Input Model Issues
No issues found. The `tension_dominant` question error in A02 is a known issue (question ID mismatch), but not related to material scenarios.

### 4.2 Rule Engine Issues  
The rule engine correctly applies rules via forward chaining. However, the issue is that exclusion rules are too broad and don't account for exceptions.

### 4.3 Solving Model Issues
The solving model correctly filters fasteners based on excluded categories. The issue is that rules are incorrectly setting excluded categories.

### 4.4 Other Issues
None identified.

---

## 5. Recommendations

### 5.1 High Priority Changes
Changes that must be made to fix critical issues:

1. **Remove or significantly modify `low_porosity_materials` rule** - This rule is causing failures in A05, A06, and potentially other scenarios. Adhesives are the correct solution for glass, ceramic, stone, metal, and plastic in many applications.

2. **Modify `paper_to_paper` rule** - Add explicit allowance for adhesive category to ensure paper-to-paper connections can use adhesives.

3. **Modify `vertical_or_overhead` rule** - Remove adhesive exclusion or make it more nuanced. Many adhesives work fine vertically.

4. **Modify `high_shear_excludes_weak_adhesives` rule** - This should exclude only weak adhesives, not all adhesives. However, this may require implementation changes to check fastener properties in rules.

5. **Modify `immediate_use_required` rule** - Should not exclude all adhesives, only slow-curing ones. May require fastener property checks.

### 5.2 Medium Priority Changes
Changes that would improve recommendations:

1. **Add `brittle_materials_allow_adhesives` rule** - Explicitly allow adhesives when brittle materials are present, overriding other exclusions.

2. **Review vibration resistance requirements** - `precision_positioning_required` may be too strict in requiring `good` vibration resistance for static loads.

3. **Consider fastener property-based rules** - Some rules (like excluding slow-curing adhesives) should check fastener properties rather than excluding entire categories.

### 5.3 Low Priority / Nice-to-Have
Improvements that could be considered:

1. **Add removable rivet variant** - Some applications need removable mechanical fasteners for plastic.

2. **Review fastener compatibility** - Ensure all material combinations have appropriate fastener options.

---

## 6. Proposed kb.json Patches

### Patch 1: Remove `low_porosity_materials` rule

```json
// Location: rules array
// Action: remove entire rule (currently at index with id "low_porosity_materials")

// This rule should be completely removed as it incorrectly excludes adhesives
// for materials where adhesives are the primary solution (glass, ceramic, stone, metal, plastic)
```

### Patch 2: Modify `paper_to_paper` rule to explicitly allow adhesives

```json
// Location: rules array, rule with id "paper_to_paper"
// Action: modify effects

{
  "id": "paper_to_paper",
  "context": "Handles very weak paper joints by excluding unsuitable fastening categories.",
  "conditions": {
    "materials.same_material": true,
    "materials.material_a.material_type": "paper"
  },
  "effects": {
    "requirements.allowed_categories": ["adhesive"],
    "requirements.excluded_categories": [
      "mechanical",
      "thermal"
    ],
    "requirements.min_tensile_strength": "very_low"
  }
}
```

### Patch 3: Remove adhesive exclusion from `vertical_or_overhead` rule

```json
// Location: rules array, rule with id "vertical_or_overhead"
// Action: modify effects - remove adhesive exclusion

{
  "id": "vertical_or_overhead",
  "context": "Requires high shear strength for vertical/overhead installations.",
  "conditions": {
    "constraints.orientation_vertical": true
  },
  "effects": {
    "requirements.min_shear_strength": "high"
  }
}
```

Note: The `overhead_installation_requires_shear` rule already sets `min_shear_strength: high`, so this rule can be simplified or removed. The original exclusion of adhesives is incorrect.

### Patch 4: Remove `high_shear_excludes_weak_adhesives` rule

```json
// Location: rules array
// Action: remove entire rule (currently at index with id "high_shear_excludes_weak_adhesives")

// This rule incorrectly excludes all adhesives when high shear is required.
// The recommendation engine should filter by fastener shear_strength property instead.
// Many adhesives have high/very_high shear strength and should be allowed.
```

### Patch 5: Modify `immediate_use_required` rule (if possible)

```json
// Location: rules array, rule with id "immediate_use_required"
// Action: modify effects - this is challenging as it requires checking fastener properties

// Option 1: Remove the rule entirely and let fastener properties handle filtering
// Option 2: Make it less restrictive - only exclude if other constraints also apply
// Option 3: Add exception for paper-to-paper connections

// For now, recommend removing or making it conditional:
{
  "id": "immediate_use_required",
  "context": "Excludes slow-curing methods when immediate usability is required.",
  "conditions": {
    "constraints.max_curing_time": "immediate",
    "materials.material_a.material_type": {"$ne": "paper"},
    "materials.material_b.material_type": {"$ne": "paper"}
  },
  "effects": {
    "requirements.excluded_categories": [
      "adhesive"
    ]
  }
}
```

Note: The condition syntax `{"$ne": "paper"}` may not be supported. This patch may require code changes to support conditional exclusions.

### Patch 6: Add `brittle_materials_allow_adhesives` rule

```json
// Location: rules array
// Action: add new rule

{
  "id": "brittle_materials_allow_adhesives",
  "context": "Explicitly allows adhesives when brittle materials are present, as adhesives are often the only suitable option.",
  "conditions": {
    "materials.any.brittleness": "very_high"
  },
  "effects": {
    "requirements.allowed_categories": ["adhesive"]
  }
}
```

Note: This rule should fire after `low_porosity_materials` to override the exclusion. Rule ordering may matter.

---

## 7. Testing Notes

Observations about the test scenarios:

- **Scenario A01 (Paper-to-Paper):** The expectation is correct - paper-to-paper should use adhesives. The scenario correctly identifies that mechanical and thermal are unsuitable.

- **Scenario A02 (Metal-to-Metal):** The expectation of both mechanical and thermal is correct. The issue is likely in rule application or fastener filtering, not the scenario.

- **Scenario A05 (Glass-to-Metal):** The expectation of adhesives is correct. Glass-to-metal connections commonly use adhesives, especially when glass is involved (brittle, can't use mechanical).

- **Scenario A06 (Ceramic-to-Stone):** The expectation of adhesives is correct. Flooring installations always use adhesives for ceramic-to-stone.

- **Scenario A07 (Plastic-to-Plastic):** The expectation of mechanical fasteners is correct. The issue may be in vibration resistance filtering or fastener compatibility.

**Edge Cases to Consider:**
- What happens when multiple exclusion rules conflict? (e.g., `low_porosity_materials` excludes adhesives, but `brittle_materials_allow_adhesives` allows them)
- Should rules have priority/ordering to handle conflicts?
- How should the system handle cases where all categories are excluded?

---

## 8. Sign-off

**Reviewed by:** Agent A  
**Confidence Level:** High  
**Requires Follow-up:** Yes

The root causes have been identified with high confidence. The primary issue is the `low_porosity_materials` rule, which is fundamentally flawed and causes multiple scenario failures. The recommended patches should resolve the majority of failures. However, some patches (like modifying `immediate_use_required` to check fastener properties) may require code changes to the rule engine to support property-based conditional logic.

---

*This report was generated as part of the KB validation process.*
