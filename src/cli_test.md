# CLI Testing Interface - Design Documentation

## Overview
Interactive command-line tool for testing the fastener recommendation system with real-time debug output.

## Usage
```bash
uv run python cli_test.py
```

## Design Choices

### Incremental Debug State Saving
The tool saves `debug_state.yaml` **after every question** to provide real-time insight into the inference process.

Allows testers to:
- Monitor the system's decision-making in real-time
- Debug issues without completing the entire questionnaire
- Understand how each answer affects recommendations

### File Structure: Holistic + Historical

The YAML file is **completely rewritten** after each answer with this structure:

```yaml
current_facts:          # All answers so far (holistic view)
current_conclusions:    # Inferred facts from rules
current_recommendations_count: N
question_history:       # Chronological list with timestamps
recommendations:        # Full details of matching fasteners
```

## Debug State Format

### 1. Current Facts
```yaml
current_facts:
  material_type: wood
  mechanical_strength: moderate
  moisture_exposure: outdoor
```
**Snapshot of all user answers at this moment**

### 2. Current Conclusions
```yaml
current_conclusions:
  recommended_categories:
    - adhesive
    - mechanical
  required_properties:
    - permanence:removable
```
**What the inference engine deduced from the rules**

### 3. Question History
```yaml
question_history:
  - question_id: material_type
    question_text: What material or surface is it intended for?
    answer: wood
    timestamp: '2025-12-12T17:07:18.742113'
```
**Complete audit trail with exact question text and timing**

### 4. Recommendations
```yaml
recommendations:
  - name: Hex bolts with nuts
    category: mechanical
    properties:
      tensile_strength: high
      water_resistance: good
      # ... all properties
    suggestions:
      - Consider stainless steel bolts for superior corrosion resistance
```
**Full details of every matching fastener with contextual suggestions**

## Testing Workflow

1. **Run the CLI** - Answer questions interactively
2. **Open `debug_state.yaml`** in another window
3. **Refresh after each answer** - See how facts accumulate
4. **Analyze conclusions** - Understand which rules fired
5. **Review recommendations** - See which fasteners match and why

## Quick Debugging

**No recommendations?**
1. Check `current_facts` - Are all required answers present?
2. Check `current_conclusions` - Did rules fire as expected?
3. Check `recommendations: []` - Review fastener properties in `kb.json`

**Wrong recommendations?**
1. Review `question_history` - Were answers interpreted correctly?
2. Check `current_conclusions` - Are the inferred properties correct?
3. Compare fastener properties to required properties

**Rule not firing?**
1. Verify all conditions in `kb.json` match the facts
2. Check rule priority (higher priority = evaluated first)
3. Look for conflicting conclusions from multiple rules

## Tips for Fresh Testers

- **Skip questions** with `s` to test partial scenarios
- **Restart** with `r` to try different answer combinations
- **Compare** multiple test runs by copying `debug_state.yaml` between runs
- The file is **always safe to open** - it's rewritten cleanly each time, never appended
