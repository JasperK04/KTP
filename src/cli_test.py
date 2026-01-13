#!/usr/bin/env python3
"""
CLI Interface for the Fastener Recommendation Knowledge System.

This CLI acts purely as a frontend. It retrieves questions from the InputModel,
displays them to the user, forwards answers back to the InputModel, and finally
displays fastener recommendations.

The CLI contains no domain knowledge, no inference logic, and no rules.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

from domain_model import (
    Fastener,
    MaterialType,
    Permanence,
    ResistanceLevel,
    Rigidity,
    StrengthLevel,
)
from input_model import InputModel
from rule_model import ForwardChainingEngine, RuleFactory
from solving_model import ProblemSolvingModel

# ─────────────────────────────────────────────
# SERIALIZATION FOR DEBUG OUTPUT
# ─────────────────────────────────────────────


def serialize_value(value):
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, set):
        return sorted(serialize_value(v) for v in value)  # pyright: ignore[reportArgumentType]
    if isinstance(value, list):
        return [serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    return value


def save_debug_state(input_model, task, recommendations, question_history):
    debug_data = {
        "timestamp": datetime.now().isoformat(),
        "answers": dict(input_model.answers),
        "derived_requirements": {
            k: serialize_value(v) for k, v in vars(task.requirements).items()
        },
        "recommendation_count": len(recommendations),
        "question_history": question_history,
        "recommendations": [],
    }

    for fastener in recommendations:
        debug_data["recommendations"].append(
            {
                "name": fastener.name,
                "category": fastener.category,
                "tensile_strength": fastener.tensile_strength.value,
                "shear_strength": fastener.shear_strength.value,
                "rigidity": fastener.rigidity.value,
                "permanence": fastener.permanence.value,
            }
        )

    with open("debug_state.yaml", "w") as f:
        yaml.dump(debug_data, f, sort_keys=False)

    return "debug_state.yaml"


# ─────────────────────────────────────────────
# QUESTION INTERACTION
# ─────────────────────────────────────────────


def ask_question(question):
    print("\n" + "-" * 80)
    print(question["text"])

    if question["type"] == "boolean":
        print("  [1] Yes")
        print("  [2] No")
        print("  [s] Skip")

        while True:
            answer = input("Your answer: ").strip().lower()
            if answer == "s":
                return None
            if answer in ("y", "yes", "1"):
                return True
            if answer in ("n", "no", "2"):
                return False
            print("Please enter 1, 2, or s.")

    elif question["type"] == "enum":
        for idx, option in enumerate(question["options"], 1):
            print(f"  [{idx}] {option}")
        print("  [s] Skip")

        while True:
            answer = input("Your answer: ").strip().lower()
            if answer == "s":
                return None
            try:
                idx = int(answer) - 1
                if 0 <= idx < len(question["options"]):
                    return question["options"][idx]
            except ValueError:
                pass
            print("Invalid choice.")

    return None


# ─────────────────────────────────────────────
# FASTENER LOADING
# ─────────────────────────────────────────────


def load_fasteners(fastener_specs):
    fasteners = []

    for spec in fastener_specs:
        fasteners.append(
            Fastener(
                name=spec["name"],
                category=spec["category"],
                compatible_materials=[
                    MaterialType(m) for m in spec["compatible_materials"]
                ],
                tensile_strength=StrengthLevel(spec["tensile_strength"]),
                shear_strength=StrengthLevel(spec["shear_strength"]),
                temperature_resistance=ResistanceLevel(spec["temperature_resistance"]),
                uv_resistance=ResistanceLevel(spec["uv_resistance"]),
                chemical_resistance=ResistanceLevel(spec["chemical_resistance"]),
                rigidity=Rigidity(spec["rigidity"]),
                permanence=Permanence(spec["permanence"]),
                water_resistance=ResistanceLevel(spec["water_resistance"]),
                vibration_resistance=ResistanceLevel(spec["vibration_resistance"]),
                requires_two_sided_access=spec["requires_two_sided_access"],
            )
        )

    return fasteners


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────


def main():
    print("=" * 80)
    print(" Fastener Recommendation System (CLI)")
    print("=" * 80)

    kb_path = Path("kb.json")
    if not kb_path.exists():
        print("Error: kb.json not found")
        sys.exit(1)

    with open(kb_path) as f:
        kb = json.load(f)

    input_model = InputModel(kb["questions"])

    rule_factory = RuleFactory(kb["rules"])
    rule_base = rule_factory.build_rule_base()
    engine = ForwardChainingEngine(rule_base)

    fasteners = load_fasteners(kb["fasteners"])
    solver = ProblemSolvingModel(engine, fasteners)

    print(len(kb["questions"]), "questions loaded.")
    print(len(kb["rules"]), "rules loaded.")
    print(len(fasteners), "fasteners loaded.")

    question_history = []

    # ─────────────────────────────────────────
    # ASK QUESTIONS
    # ─────────────────────────────────────────

    while True:
        question = input_model.get_next_question()
        if question is None:
            break

        answer = ask_question(question)

        if answer is not None:
            input_model.answer_question(question["id"], answer)
            question_history.append(
                {
                    "question_id": question["id"],
                    "question_text": question["text"],
                    "answer": answer,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    # ─────────────────────────────────────────
    # SOLVE
    # ─────────────────────────────────────────

    task = input_model.get_task()
    recommendations = solver.recommend(task)

    print("\n" + "=" * 80)
    if not recommendations:
        print("❌ No suitable fasteners found.")
    else:
        print(f"✅ Found {len(recommendations)} suitable fastener(s):\n")
        for idx, f in enumerate(recommendations, 1):
            print(f"{idx}. {f.name}")
            print(f"   Category: {f.category}")
            print(f"   Tensile Strength: {f.tensile_strength.value}")
            print(f"   Rigidity: {f.rigidity.value}")
            print(f"   Permanence: {f.permanence.value}")
            print()

    debug_file = save_debug_state(input_model, task, recommendations, question_history)
    print(f"\n📝 Debug state saved to {debug_file}")
    print("\nThank you for using the system.")


if __name__ == "__main__":
    main()
