# Future Enhancement: Set-Theory Based Matching and Ranking

## Current Implementation (v1)
The current inference engine uses **binary boolean filtering**:
- Each fastener either passes ALL requirements or is disqualified
- All qualifying fasteners are considered equally valid
- No ranking or preference differentiation

## Proposed Enhancement: Set-Theory Intersection Scoring

### Core Concept
Model the recommendation problem as **set intersection maximization**:

```
User Requirements = Set of (question_id, answer_value) pairs
Fastener Capabilities = Set of conditions the fastener satisfies

Match Quality = |User Requirements ∩ Fastener Capabilities|
                (cardinality of intersection)
```

### Mathematical Foundation

Given:
- U = User facts (finite set of condition-value pairs)
- F = Fastener's satisfiable conditions (finite set)
- Score(fastener) = |U ∩ F|

Ranking: Sort fasteners by descending intersection cardinality.

### Example Scenario

**User Requirements:**
```
U = {
  (material_type, wood),
  (mechanical_strength, moderate),
  (moisture_exposure, outdoor),
  (permanence, removable)
}
```

**Fastener A (Wood Screws):**
```
F_A = {
  (material_type, wood),           // Match
  (mechanical_strength, moderate),  // Match
  (moisture_exposure, outdoor),     // Match (coated variants)
  (permanence, removable)           // Match
}
Score(A) = |U ∩ F_A| = 4
```

**Fastener B (Wood Glue):**
```
F_B = {
  (material_type, wood),            // Match
  (mechanical_strength, moderate),   // Match
  (moisture_exposure, no),           // No match (poor water resistance)
  (permanence, semi_permanent)       // No match
}
Score(B) = |U ∩ F_B| = 2
```

**Result:** Wood Screws (4) ranked higher than Wood Glue (2)

## Benefits

### 1. Natural Ranking
- Provides intuitive ordering: "best fit" comes first
- Eliminates the all-or-nothing limitation of binary matching
- Users see fasteners ranked by compatibility, not just yes/no

### 2. Negation as Set Complement
Handling "NOT" conditions becomes mathematically clean:

```
moisture_exposure: {not: [outdoor, submerged]}
  ≡ moisture_exposure ∈ (AllMoistureChoices \ {outdoor, submerged})
  ≡ moisture_exposure ∈ {no, splash}
```

Implementation:
```python
if condition is negation:
    all_choices = get_question_choices(question_id)
    valid_set = set(all_choices) - set(excluded_values)
    matches = actual_value in valid_set
```

### 3. Transparent Scoring
Users can understand why fastener X ranks higher than Y:
- "Wood screws match 4 of your 5 requirements"
- "Wood glue matches only 2 of your 5 requirements"

### 4. Graceful Degradation
If no fastener perfectly matches all requirements, the system still provides useful recommendations ranked by partial match quality rather than returning empty results.

## Challenges and Solutions

### Challenge 1: Not All Conditions Are Equal Weight

**Problem:** Material incompatibility is a hard failure, but curing time preference is soft.

**Solution - Hybrid Approach:**
```python
def recommend_fasteners(self):
    results = []
    
    for fastener in self.kb.fasteners:
        # Phase 1: Hard requirements (binary pass/fail)
        if not meets_critical_requirements(fastener):
            continue  # Disqualify immediately
        
        # Phase 2: Soft preferences (set intersection score)
        preference_score = calculate_preference_intersection(fastener)
        
        results.append((fastener, preference_score))
    
    return sorted(results, key=lambda x: x[1], reverse=True)
```

**Critical requirements (must pass):**
- Material compatibility
- Minimum strength thresholds (ordinal comparison)
- Safety-critical properties (chemical resistance in corrosive environments)

**Soft preferences (scored by intersection):**
- Curing time preferences
- Removability vs permanence
- Tool requirements
- Convenience factors

### Challenge 2: Ordinal vs Nominal Comparison

**Problem:** Some properties are ordinal (strength: low < moderate < high), not just set membership.

**Solution:** Extend set theory with ordinal logic:
```python
def satisfies_condition(fastener, question_id, user_value):
    if is_ordinal_scale(question_id):
        # Ordinal: fastener must meet or exceed requirement
        return fastener_value >= user_value
    else:
        # Nominal: exact set membership
        return user_value in fastener.valid_values
```

### Challenge 3: Multi-Valued Properties

**Problem:** A fastener's `compatible_materials` is itself a set, not a single value.

**Solution:** Treat as subset relationship:
```python
# User wants to fasten wood
user_material = "wood"

# Fastener compatible with [wood, plastic, metal]
fastener_materials = ["wood", "plastic", "metal"]

# Match if user's material is in fastener's compatible set
matches = user_material in fastener_materials
```

## Implementation Sketch

```python
class InferenceEngine:
    def calculate_match_score(self, fastener: Fastener) -> tuple[bool, int]:
        """
        Returns:
            (passes_hard_requirements, soft_preference_score)
        """
        # Phase 1: Hard requirements
        if not self.check_material_compatibility(fastener):
            return (False, 0)
        
        if not self.check_minimum_strength(fastener):
            return (False, 0)
        
        if not self.check_safety_critical_properties(fastener):
            return (False, 0)
        
        # Phase 2: Count preference matches
        preference_matches = 0
        
        for fact_key, fact_value in self.facts.items():
            if fact_key in self.soft_preference_facts:
                if self.fastener_satisfies(fastener, fact_key, fact_value):
                    preference_matches += 1
        
        return (True, preference_matches)
    
    def recommend_fasteners(self) -> list[tuple[Fastener, int, list[str]]]:
        self.infer()
        
        results = []
        for fastener in self.kb.fasteners:
            passes, score = self.calculate_match_score(fastener)
            
            if passes:
                suggestions = self.get_suggestions(fastener)
                results.append((fastener, score, suggestions))
        
        # Rank by preference score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results
```

## Knowledge Base Schema Extension

To support this, add metadata to questions distinguishing hard vs soft requirements:

```json
{
  "questions": [
    {
      "id": "material_type",
      "text": "What material or surface is it intended for?",
      "answer_type": "choice",
      "choices": ["wood", "metal", "masonry", ...],
      "requirement_type": "hard"  // NEW: This is critical
    },
    {
      "id": "curing_time",
      "text": "What is the acceptable curing/drying time?",
      "answer_type": "choice",
      "choices": ["immediate", "minutes", "hours", "days"],
      "requirement_type": "soft"  // NEW: This is a preference
    }
  ]
}
```

## Migration Path

1. **Phase 1 (Current):** Binary boolean filtering - get basic system working
2. **Phase 2:** Add negation support to conditions (set complement)
3. **Phase 3:** Implement preference scoring using set intersection
4. **Phase 4:** Add requirement_type metadata to questions
5. **Phase 5:** Full hybrid hard/soft scoring implementation

## Why Not Implement Now?

**Current priority:** Establish solid foundation with binary matching:
- Validate rule structure and logic
- Ensure data-driven approach works
- Test with real use cases
- Gather user feedback

**Premature optimization risk:**
- More complex to debug
- Harder to validate correctness
- May solve a problem users don't actually have
- Could over-engineer before understanding actual needs

**Principle:** Make it work, make it right, make it fast (in that order).

## Related Concepts

- **Information Retrieval:** TF-IDF scoring, BM25 ranking
- **Constraint Satisfaction:** Hard constraints vs optimization objectives
- **Multi-Criteria Decision Analysis:** Weighted scoring of alternatives
- **Recommender Systems:** Content-based filtering with feature matching

## References for Future Implementation

- Russell & Norvig, "Artificial Intelligence: A Modern Approach" - Chapter on Constraint Satisfaction Problems
- Set theory basics: union, intersection, complement operations
- Jaccard similarity coefficient: |A ∩ B| / |A ∪ B|
- Consider weighted Jaccard if different facts should have different importance

---

**Status:** Design document for future iteration  
**Priority:** Medium (after core system is stable)  
**Dependencies:** Binary matching system must be working and validated first
