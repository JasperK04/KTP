#!/usr/bin/env python3
"""
Scenario Runner for KB Testing.

Executes all test scenarios and exports results per agent for review.
Each agent gets a separate YAML file with their assigned scenarios' results.

Usage:
    python tests/run_scenarios.py

Output:
    tests/results/agent_a_results.yaml
    tests/results/agent_b_results.yaml
    tests/results/agent_c_results.yaml
    tests/results/agent_d_results.yaml
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.kb_scenarios import (
    ALL_SCENARIOS,
    TestScenario,
    get_scenarios_for_agent,
)
from src.domain_model import Fastener
from src.input_model import InputModel
from src.rule_model import ForwardChainingEngine, RuleFactory
from src.solving_model import ProblemSolvingModel


def serialize_value(value):
    """Convert enums and sets to serializable formats."""
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, set):
        return sorted(serialize_value(v) for v in value)
    if isinstance(value, list):
        return [serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    return value


def run_scenario(
    scenario: TestScenario,
    kb: dict,
) -> dict:
    """
    Execute a single scenario and return detailed results.
    
    Returns dict with:
        - scenario info
        - answers applied
        - derived requirements
        - fired rules
        - recommended fasteners
        - evaluation (pass/fail for expectations)
    """
    # Fresh instances for each scenario
    input_model = InputModel(kb["questions"], kb["materials"])
    
    rule_factory = RuleFactory(kb["rules"])
    rule_base = rule_factory.build_rule_base()
    engine = ForwardChainingEngine(rule_base)
    
    fasteners = [Fastener.from_dict(f) for f in kb["fasteners"]]
    solver = ProblemSolvingModel(engine, fasteners)
    
    # Apply answers from scenario
    errors = []
    for question_id, answer in scenario.answers.items():
        try:
            # Check if question exists
            question = None
            for q in kb["questions"]:
                if q["id"] == question_id:
                    question = q
                    break
            
            if question is None:
                errors.append(f"Unknown question: {question_id}")
                continue
                
            # Check if question is applicable
            if not input_model.is_question_applicable(question):
                # Skip conditional questions that don't apply
                continue
                
            input_model.answer_question(question_id, answer)
        except Exception as e:
            errors.append(f"Error answering {question_id}: {str(e)}")
    
    # Get recommendations
    task = input_model.get_task()
    recommendations = solver.recommend(task)
    
    # Build results
    recommended_names = [f.name for f in recommendations]
    recommended_categories = list(set(f.category for f in recommendations))
    
    # Evaluate expectations
    evaluation = {
        "expected_categories_found": [],
        "expected_categories_missing": [],
        "excluded_categories_violated": [],
        "expected_fasteners_found": [],
        "expected_fasteners_missing": [],
        "unexpected_fasteners_found": [],
    }
    
    for cat in scenario.expected_categories:
        if cat in recommended_categories:
            evaluation["expected_categories_found"].append(cat)
        else:
            evaluation["expected_categories_missing"].append(cat)
    
    for cat in scenario.excluded_categories:
        if cat in recommended_categories:
            evaluation["excluded_categories_violated"].append(cat)
    
    for fastener in scenario.expected_fasteners:
        if fastener in recommended_names:
            evaluation["expected_fasteners_found"].append(fastener)
        else:
            evaluation["expected_fasteners_missing"].append(fastener)
    
    for fastener in scenario.unexpected_fasteners:
        if fastener in recommended_names:
            evaluation["unexpected_fasteners_found"].append(fastener)
    
    # Determine pass/fail
    passed = (
        len(evaluation["expected_categories_missing"]) == 0 and
        len(evaluation["excluded_categories_violated"]) == 0 and
        len(evaluation["unexpected_fasteners_found"]) == 0
    )
    
    return {
        "scenario_id": scenario.id,
        "scenario_name": scenario.name,
        "description": scenario.description,
        "notes": scenario.notes,
        "answers_applied": scenario.answers,
        "errors": errors,
        "derived_requirements": {
            k: serialize_value(v) 
            for k, v in vars(task.requirements).items()
        },
        "fired_rules": sorted(engine.fired_rules),
        "recommendations": [
            {
                "name": f.name,
                "category": f.category,
                "tensile_strength": f.tensile_strength.value,
                "shear_strength": f.shear_strength.value,
                "rigidity": f.rigidity.value,
                "permanence": f.permanence.value,
                "water_resistance": f.water_resistance.value,
                "vibration_resistance": f.vibration_resistance.value,
            }
            for f in recommendations
        ],
        "recommendation_count": len(recommendations),
        "recommended_categories": recommended_categories,
        "evaluation": evaluation,
        "passed": passed,
    }


def run_all_scenarios(kb: dict) -> dict[str, list[dict]]:
    """Run all scenarios and group results by agent."""
    results_by_agent = {
        "A": [],
        "B": [],
        "C": [],
        "D": [],
    }
    
    for scenario in ALL_SCENARIOS:
        print(f"Running scenario {scenario.id}: {scenario.name}...")
        result = run_scenario(scenario, kb)
        results_by_agent[scenario.agent].append(result)
        
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status} - {result['recommendation_count']} recommendations")
    
    return results_by_agent


def export_results(results_by_agent: dict[str, list[dict]], output_dir: Path):
    """Export results to YAML files per agent."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for agent, results in results_by_agent.items():
        passed = sum(1 for r in results if r["passed"])
        failed = len(results) - passed
        
        output_data = {
            "agent": agent,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_scenarios": len(results),
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{100 * passed / len(results):.1f}%" if results else "N/A",
            },
            "scenarios": results,
        }
        
        filename = output_dir / f"agent_{agent.lower()}_results.yaml"
        with open(filename, "w") as f:
            yaml.dump(output_data, f, sort_keys=False, default_flow_style=False, width=120)
        
        print(f"Exported Agent {agent} results to {filename}")


def main():
    print("=" * 80)
    print(" KB Scenario Test Runner")
    print("=" * 80)
    
    # Load knowledge base
    kb_path = Path(__file__).resolve().parent.parent / "src" / "kb.json"
    if not kb_path.exists():
        print(f"Error: kb.json not found at {kb_path}")
        sys.exit(1)
    
    with open(kb_path) as f:
        kb = json.load(f)
    
    print(f"\nLoaded KB with:")
    print(f"  - {len(kb['questions'])} questions")
    print(f"  - {len(kb['rules'])} rules")
    print(f"  - {len(kb['fasteners'])} fasteners")
    print(f"  - {len(kb['materials'])} materials")
    print(f"\nRunning {len(ALL_SCENARIOS)} test scenarios...\n")
    
    # Run scenarios
    results_by_agent = run_all_scenarios(kb)
    
    # Export results
    output_dir = Path(__file__).resolve().parent / "results"
    export_results(results_by_agent, output_dir)
    
    # Print summary
    print("\n" + "=" * 80)
    print(" SUMMARY")
    print("=" * 80)
    
    total_passed = 0
    total_failed = 0
    
    for agent in ["A", "B", "C", "D"]:
        results = results_by_agent[agent]
        passed = sum(1 for r in results if r["passed"])
        failed = len(results) - passed
        total_passed += passed
        total_failed += failed
        
        print(f"\nAgent {agent}: {passed}/{len(results)} passed")
        
        for r in results:
            status = "✓" if r["passed"] else "✗"
            print(f"  {status} {r['scenario_id']}: {r['scenario_name']}")
            
            if not r["passed"]:
                eval_info = r["evaluation"]
                if eval_info["expected_categories_missing"]:
                    print(f"      Missing categories: {eval_info['expected_categories_missing']}")
                if eval_info["excluded_categories_violated"]:
                    print(f"      Violated exclusions: {eval_info['excluded_categories_violated']}")
                if eval_info["unexpected_fasteners_found"]:
                    print(f"      Unexpected fasteners: {eval_info['unexpected_fasteners_found']}")
    
    print(f"\n{'=' * 80}")
    print(f"TOTAL: {total_passed}/{total_passed + total_failed} scenarios passed")
    print(f"{'=' * 80}")
    
    print(f"\nResults exported to: {output_dir}/")
    print("Each agent should review their respective results file.")


if __name__ == "__main__":
    main()
