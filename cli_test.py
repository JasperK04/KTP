#!/usr/bin/env python3
"""
CLI Testing Interface for Fastener Recommendation System
Asks questions interactively and provides recommendations with debug output
"""

import sys
from datetime import datetime
from pathlib import Path

import yaml

from src.engine import InferenceEngine, KnowledgeBase, QuestionType


def save_debug_state(
    engine: InferenceEngine,
    question_history: list = None,
    filename: str = "debug_state.yaml",
):
    """Save current facts, conclusions, and recommendations to YAML for debugging"""
    recommendations = engine.recommend_fasteners()

    debug_data = {
        "current_facts": dict(engine.facts),
        "current_conclusions": dict(engine.conclusions),
        "current_recommendations_count": len(recommendations),
    }

    if question_history:
        debug_data["question_history"] = question_history

    debug_data["recommendations"] = []
    for fastener, suggestions in recommendations:
        rec = {
            "name": fastener.name,
            "category": fastener.category.value,
            "properties": {
                "compatible_materials": fastener.properties.compatible_materials,
                "tensile_strength": fastener.properties.tensile_strength.value,
                "shear_strength": fastener.properties.shear_strength.value,
                "compressive_strength": fastener.properties.compressive_strength.value,
                "water_resistance": fastener.properties.water_resistance.value,
                "weather_resistance": fastener.properties.weather_resistance.value,
                "chemical_resistance": fastener.properties.chemical_resistance.value,
                "temperature_resistance": fastener.properties.temperature_resistance.value,
                "vibration_resistance": fastener.properties.vibration_resistance.value,
                "rigidity": fastener.properties.rigidity.value,
                "permanence": fastener.properties.permanence.value,
                "notes": fastener.properties.notes,
            },
            "requires_tools": fastener.requires_tools,
            "surface_prep": fastener.surface_prep,
            "curing_time": fastener.curing_time,
            "suggestions": suggestions,
        }
        debug_data["recommendations"].append(rec)

    with open(filename, "w") as f:
        yaml.dump(debug_data, f, default_flow_style=False, sort_keys=False)

    return filename


def ask_question(question, engine: InferenceEngine, question_history: list) -> any:
    """Ask a single question and get user input, saving debug state after each answer"""
    print(f"\n{question.text}")

    if question.type == QuestionType.BOOLEAN:
        print("  [y] Yes")
        print("  [n] No")
        print("  [s] Skip")

        while True:
            answer = input("Your answer: ").strip().lower()
            if answer == "s":
                return None
            elif answer in ["y", "yes"]:
                answer_value = True
                break
            elif answer in ["n", "no"]:
                answer_value = False
                break
            else:
                print("Invalid input. Please enter 'y', 'n', or 's' to skip.")

    elif question.type == QuestionType.CHOICE:
        for idx, choice in enumerate(question.choices, 1):
            print(f"  [{idx}] {choice}")
        print("  [s] Skip")

        while True:
            answer = input("Your answer (number or 's' to skip): ").strip().lower()
            if answer == "s":
                return None
            try:
                choice_idx = int(answer) - 1
                if 0 <= choice_idx < len(question.choices):
                    answer_value = question.choices[choice_idx]
                    break
                else:
                    print(
                        f"Please enter a number between 1 and {len(question.choices)}, or 's' to skip."
                    )
            except ValueError:
                print("Invalid input. Please enter a number or 's' to skip.")
    else:
        return None

    question_history.append(
        {
            "question_id": question.id,
            "question_text": question.text,
            "answer": answer_value,
            "timestamp": datetime.now().isoformat(),
        }
    )

    save_debug_state(engine, question_history)
    print(f"  ✓ Debug state updated (questions answered: {len(question_history)})")

    return answer_value


def display_recommendations(recommendations: list):
    """Display fastener recommendations in a readable format"""
    if not recommendations:
        print("\n❌ No fasteners match your requirements.")
        print("Try adjusting your requirements or using different materials.")
        return

    print(f"\n✅ Found {len(recommendations)} matching fastener(s):\n")
    print("=" * 80)

    for idx, (fastener, suggestions) in enumerate(recommendations, 1):
        print(f"\n{idx}. {fastener.name}")
        print(f"   Category: {fastener.category.value}")
        print(
            f"   Compatible Materials: {', '.join(fastener.properties.compatible_materials)}"
        )
        print(f"   Strength: {fastener.properties.tensile_strength.value}")
        print(f"   Water Resistance: {fastener.properties.water_resistance.value}")
        print(f"   Permanence: {fastener.properties.permanence.value}")
        print(f"   Rigidity: {fastener.properties.rigidity.value}")

        if fastener.curing_time:
            print(f"   Curing Time: {fastener.curing_time}")

        if fastener.requires_tools:
            print(f"   Required Tools: {', '.join(fastener.requires_tools)}")

        if fastener.surface_prep:
            print(f"   Surface Prep: {', '.join(fastener.surface_prep)}")

        if suggestions:
            print("\n   💡 Suggestions:")
            for suggestion in suggestions:
                print(f"      • {suggestion}")

        if fastener.properties.notes:
            print("\n   📝 Notes:")
            for note in fastener.properties.notes:
                print(f"      • {note}")

        print()


def main():
    print("=" * 80)
    print("  Fastener Recommendation System - CLI Test Interface")
    print("=" * 80)

    kb_path = Path(__file__).parent / "src" / "kb.json"
    if not kb_path.exists():
        print(f"Error: Knowledge base not found at {kb_path}")
        sys.exit(1)

    kb = KnowledgeBase()
    kb.load_from_file(str(kb_path))

    print("\nLoaded knowledge base:")
    print(f"  - {len(kb.questions)} questions")
    print(f"  - {len(kb.fasteners)} fasteners")
    print(f"  - {len(kb.rules)} rules")
    print(f"  - {len(kb.suggestion_rules)} suggestion rules")

    engine = InferenceEngine(kb)
    question_history = []

    print("\n" + "=" * 80)
    print("Answer questions to get fastener recommendations")
    print("(You can skip any question by entering 's')")
    print("(Debug state saved after each answer to debug_state.yaml)")
    print("=" * 80)

    while True:
        asked = {q["question_id"] for q in question_history}
        question = engine.select_next_question(asked)

        if question is None:
            break

        answer = ask_question(question, engine, question_history)
        if answer is not None:
            engine.add_fact(question.id, answer)

    print("\n" + "=" * 80)
    print("  Generating Recommendations...")
    print("=" * 80)

    recommendations = engine.recommend_fasteners()
    display_recommendations(recommendations)

    debug_file = save_debug_state(engine, question_history)
    print("\n" + "=" * 80)
    print(f"✅ Final debug state saved to: {debug_file}")
    print("=" * 80)

    print("\nOptions:")
    print("  [r] Restart with new answers")
    print("  [q] Quit")

    choice = input("\nYour choice: ").strip().lower()
    if choice == "r":
        engine.reset()
        main()
    else:
        print("\nThank you for using the Fastener Recommendation System!")


if __name__ == "__main__":
    main()
