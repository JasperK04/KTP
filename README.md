# Fastener Recommendation System

An expert system for recommending fastening methods based on material properties, strength requirements, and environmental conditions.

## Requirements
- Python 3.12+
- uv (Python package manager)

## Installation

```bash
uv sync
```

## Usage

### CLI Testing Interface

Interactive command-line interface for testing the recommendation engine:

```bash
uv run python cli_test.py
```

This will:
- Ask you a series of questions about your fastening requirements
- **Save debug state after each question** to `debug_state.yaml`
- Generate final recommendations based on your answers
- Provide complete audit trail with timestamps

The debug file includes:
- Current facts (all answers so far)
- Current conclusions from inference rules
- Question history with timestamps
- Complete recommendation details

### Web Interface

Run the Flask web application:

```bash
uv run python main.py
```

Or for development with auto-reload:

```bash
uv run flask run --debug
```

### Running Tests

Run the complete test suite:

```bash
uv run pytest
```

Run with verbose output:

```bash
uv run pytest -v
```

## Project Structure

- `src/engine.py` - Core inference engine and knowledge base
- `src/kb.json` - Knowledge base (questions, fasteners, rules, suggestion rules)
- `src/app/` - Flask web application
- `cli_test.py` - CLI testing interface (root level)
- `cli_test.md` - CLI testing documentation and design rationale
- `main.py` - Web application entry point (root level)
- `tests/` - Test suite (89 tests, root level)
- `debug_state.yaml` - Generated debug output (updated after each question)

## Debugging

The CLI tool automatically updates `debug_state.yaml` **after every question**. This file contains:

```yaml
current_facts:              # All answers provided so far
current_conclusions:        # Inferred facts from rules
current_recommendations_count: N
question_history:           # Complete audit trail with timestamps
recommendations:            # Matching fasteners with full details
```

Use this file to:
- Monitor the inference process in real-time
- Debug why certain fasteners were/weren't recommended
- Understand which rules fired and when
- Verify the inference logic step-by-step
- Track the complete recommendation process with timestamps

See `cli_test.md` for detailed documentation on the debug format and testing workflow.