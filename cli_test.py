#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

from src.domain_model import (
    Fastener,
    MaterialType,
    Permanence,
    ResistanceLevel,
    Rigidity,
    StrengthLevel,
)
from src.input_model import InputModel
from src.rule_model import ForwardChainingEngine, RuleFactory
from src.solving_model import ProblemSolvingModel


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
        "question_history": list(question_history),
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

    filename = "debug_state.yaml"
    with open(filename, "w") as f:
        yaml.dump(debug_data, f, sort_keys=False)

    return filename


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


def main():
    print("=" * 80)
    print(" Fastener Recommendation System (CLI)")
    print("=" * 80)

    kb_path = Path(__file__).resolve().parent / "src" / "kb.json"
    if not kb_path.exists():
        print("Error: kb.json not found")
        sys.exit(1)

    with open(kb_path) as f:
        kb = json.load(f)

    input_model = InputModel(kb["questions"], kb["materials"])

    rule_factory = RuleFactory(kb["rules"])
    rule_base = rule_factory.build_rule_base()
    engine = ForwardChainingEngine(rule_base)

    fasteners = load_fasteners(kb["fasteners"])
    solver = ProblemSolvingModel(engine, fasteners)

    question_history = []

    print(f"\nloaded {len(kb['questions'])} questions from knowledge base.")
    print(f"loaded {len(kb['rules'])} rules from knowledge base.")
    print(f"loaded {len(kb['materials'])} materials from knowledge base.")
    print(f"loaded {len(kb['fasteners'])} fasteners from knowledge base.")

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

            task = input_model.get_task()
            recommendations = solver.recommend(task)

            save_debug_state(input_model, task, recommendations, question_history)

    task = input_model.get_task()
    recommendations = solver.recommend(task)

    print("\n" + "=" * 80)
    if not recommendations:
        print("❌ No suitable fasteners found.")
    else:
        print(f"Found {len(recommendations)} suitable fastener(s):\n")
        for idx, f in enumerate(recommendations, 1):
            print(f"{idx}. {f.name}")
            print(f"   Category: {f.category}")
            print(f"   Tensile Strength: {f.tensile_strength.value}")
            print(f"   Rigidity: {f.rigidity.value}")
            print(f"   Permanence: {f.permanence.value}")
            print()

    final_debug = save_debug_state(input_model, task, recommendations, question_history)

    print(f"\nFinal debug state saved to {final_debug}")
    print("\nThank you for using the system.")


if __name__ == "__main__":
    main()
