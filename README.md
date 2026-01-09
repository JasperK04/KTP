# Fastener Recommendation System

An expert system for recommending fastening methods based on material properties, strength requirements, and environmental conditions.

## Requirements
- Python 3.12+
- uv (Python package manager) or pip

## Installation
### using uv 
```bash
uv sync
```
### using pip
```bash
pip install -r requirements.txt
```

## Usage

### Activate your virtual environment

```bash
source .venv/bin/activate
```

### CLI Testing Interface

Interactive command-line interface for testing the recommendation engine:

```bash
python cli_test.py
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

The web-based interface is provided through a Flask application.  
You can start the application using either of the following commands:

```bash
python main.py
```
or
```bash
flask run
```

Both commands support the same runtime options:
- `--debug`, Starts the application in development mode with automatic reloading enabled.
- `--port <port>`, Runs the application on the specified available port.

```bash
python main.py --debug --port 5001
```
```bash
flask run --debug --port 5001
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
- `tests/` - Test suite (80 tests, root level)
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
