# Test Suite Overview

**89 tests** organized across 4 test files + shared fixtures

## Test Files

### `conftest.py`
Shared pytest fixtures:
- `kb_path` - Path to src/kb.json
- `kb` - Pre-loaded KnowledgeBase
- `empty_kb` - Empty KnowledgeBase instance

### `test_models.py` (20 tests)
Dataclass model tests:
- `TestQuestionModel` - Question serialization/deserialization
- `TestMaterialPropertiesModel` - MaterialProperties validation
- `TestFastenerModel` - Fastener model validation
- `TestRuleModel` - Rule model validation
- `TestSuggestionRuleModel` - SuggestionRule validation

### `test_knowledge_base.py` (19 tests)
KnowledgeBase operations:
- `TestKnowledgeBaseInitialization` - Empty KB initialization
- `TestKnowledgeBaseLoading` - Loading from src/kb.json
- `TestKnowledgeBaseSaving` - Saving/reloading data integrity

### `test_inference_engine.py` (33 tests)
Inference logic:
- `TestInferenceEngineInitialization` - Engine setup
- `TestFactManagement` - Adding/managing facts
- `TestRuleEvaluation` - Rule condition evaluation
- `TestRuleApplication` - Applying rule conclusions
- `TestForwardChainingInference` - Forward-chaining algorithm
- `TestFastenerMatching` - Fastener filtering logic
- `TestSuggestionGeneration` - Contextual suggestions
- `TestFastenerRecommendation` - End-to-end recommendations

### `test_ordinal_scales.py` (17 tests)
Ordinal scale logic:
- `TestOrdinalScales` - Scale definitions and mappings
- `TestStrengthEnum` - Strength enum validation
- `TestResistanceEnum` - Resistance enum validation
- `TestOrdinalComparisons` - Ordinal comparison logic

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_models.py

# Run specific test class
uv run pytest tests/test_models.py::TestQuestionModel
```
