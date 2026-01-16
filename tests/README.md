# Test Suite Documentation

This document describes the **pytest-based verification and validation suite** for the Fastener Recommendation Knowledge System. It is intended to explain the *purpose, structure, and coverage* of the tests, not the internal implementation of the models themselves.

The test suite serves two roles within the Knowledge Technology Practical (KTP):

* **Verification** – checking that the system behaves according to its specification
* **Validation** – checking that the implemented reasoning matches the intended knowledge-level behavior

---

## 1. Scope of the Test Suite

The tests focus on **behavioral correctness**, not UI concerns. In particular, they verify:

* Correct construction and serialization of domain objects
* Correct evaluation and firing of rules
* Correct forward‑chaining inference behavior
* Monotonic reasoning over ordinal scales
* Proper isolation between components
* End‑to‑end reasoning flow from task to recommendation

The tests do not aim to re‑test Python internals or dataclass mechanics beyond what is relevant for knowledge reasoning.

---

## 2. Test Structure

```text
tests/
├── conftest.py
├── test_domain_model.py
├── test_rule_model.py
├── test_inference_engine.py
├── test_input_model.py
├── test_solving_model.py
```

Each test file targets a specific responsibility in the system.

---

## 3. Shared Fixtures (`conftest.py`)

`conftest.py` defines reusable pytest fixtures to avoid duplication and ensure consistency.

Key fixtures include:

* **Knowledge base loading** – loading `kb.json` once and reusing it
* **Pre‑constructed domain objects** – materials, tasks, and fasteners
* **Initialized engines** – rule engines and input models backed by real KB data

This ensures that most tests operate on *realistic system state* rather than artificial mocks, unless isolation is explicitly required.

---

## 4. Domain Model Tests (`test_domain_model.py`)

These tests verify that domain objects:

* Correctly round‑trip via `to_dict()` / `from_dict()`
* Correctly use enum values and ordinal levels
* Preserve equality after serialization

The goal is to ensure that domain objects are stable, serializable knowledge carriers, which is essential for debugging, persistence, and state restoration.

---

## 5. Rule Model Tests (`test_rule_model.py`)

These tests focus on rule construction and execution semantics:

* Rules are correctly built from declarative specifications
* Conditions evaluate to True/False as expected
* Effects correctly update task state
* Ordinal effects are applied monotonically (never weakening requirements)
* Rules fire at most once

The tests explicitly check that later rules cannot override stronger earlier conclusions.

---

## 6. Inference Engine Tests (`test_inference_engine.py`)

These tests isolate the forward‑chaining algorithm itself, using `MagicMock` rules.

They verify:

* Single‑rule inference
* Multi‑rule forward chaining
* No re‑firing of rules
* Rule‑order independence

By mocking rules, these tests ensure that failures can be attributed to the engine logic, not the domain or rule factory.

---

## 7. Input Model Tests (`test_input_model.py`)

The input model tests verify the question asking logic:

* Questions are asked in the correct order
* Answering a question updates the correct attribute
* Enum coercion is applied correctly
* Applicability conditions (`ask_if`) are respected

These tests ensure that user input is translated into domain knowledge in a controlled and predictable way.

---

## 8. Problem Solving Model Tests (`test_solving_model.py`)

These tests verify the end‑to‑end reasoning pipeline, while still keeping components isolated where necessary.

They cover:

* Candidate filtering by category, rigidity, strength, and resistance
* One‑sided vs two‑sided access constraints
* Proper interaction between inference and evaluation phases
* Full `recommend()` flow using a mocked inference engine

The emphasis is on knowledge‑level correctness: given certain inferred requirements, the correct fasteners must be selected or rejected.

---

## 9. Use of Mocks

Mocks are used only where appropriate, primarily to:

* Isolate the forward‑chaining engine
* Simulate inferred requirements without relying on specific rules
* Avoid brittle cross‑dependencies between tests

---

## 10. Running the Tests

From the project root:

```bash
uv run pytest
```

Verbose output:

```bash
uv run pytest -v
```

All tests are designed to be deterministic and order‑independent.
