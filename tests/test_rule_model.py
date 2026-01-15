import pytest

from domain_model import (
    Environment,
    FasteningTask,
    LoadCondition,
    LoadType,
    Material,
    MaterialPair,
    MaterialType,
    MoistureExposure,
    Permanence,
    ResistanceLevel,
    StrengthLevel,
    UsageConstraints,
)
from rule_model import ForwardChainingEngine, RuleBase, RuleFactory


def make_empty_task():
    return FasteningTask(
        materials=MaterialPair(
            Material(MaterialType.WOOD, "medium", "medium", StrengthLevel.MODERATE),
            Material(MaterialType.WOOD, "medium", "medium", StrengthLevel.MODERATE),
        ),
        environment=Environment(
            moisture=MoistureExposure.NONE,
            chemical_exposure=False,
            uv_exposure=False,
            temperature_extremes=False,
        ),
        load=LoadCondition(
            load_type=LoadType.STATIC,
            vibration=False,
            tension_dominant=False,
            shock_loads=False,
        ),
        constraints=UsageConstraints(
            permanence=Permanence.SEMI_PERMANENT,
            flexibility_required=False,
            orientation_vertical=False,
            precision_required=False,
            health_constraints=False,
            one_side_accessable=False,
            max_curing_time=None,
        ),
    )


def test_rule_factory_builds_rule_base():
    specs = [
        {
            "id": "test_rule",
            "conditions": {"environment.moisture": MoistureExposure.OUTDOOR},
            "effects": {"requirements.min_water_resistance": ResistanceLevel.GOOD},
        }
    ]

    factory = RuleFactory(specs)
    rule_base = factory.build_rule_base()

    assert isinstance(rule_base, RuleBase)
    assert len(rule_base.rules) == 1
    assert rule_base.rules[0].id == "test_rule"


def test_condition_evaluation_true_when_conditions_match():
    specs = [
        {
            "id": "moisture_rule",
            "conditions": {"environment.moisture": "outdoor"},
            "effects": {"requirements.min_water_resistance": "good"},
        }
    ]

    task = make_empty_task()
    task.environment.moisture = MoistureExposure.OUTDOOR

    rules = RuleFactory(specs).build_rule_base()
    engine = ForwardChainingEngine(rules)
    engine.infer(task)

    assert task.requirements.min_water_resistance is ResistanceLevel.GOOD


def test_condition_evaluation_false_when_conditions_do_not_match():
    specs = [
        {
            "id": "moisture_rule",
            "conditions": {"environment.moisture": MoistureExposure.OUTDOOR},
            "effects": {"requirements.min_water_resistance": ResistanceLevel.GOOD},
        }
    ]

    task = make_empty_task()

    engine = ForwardChainingEngine(RuleFactory(specs).build_rule_base())
    engine.infer(task)

    assert task.requirements.min_water_resistance is ResistanceLevel.NONE


def test_action_execution_is_monotonic_for_strength_levels():
    specs = [
        {
            "id": "moderate_strength",
            "conditions": {"load.load_type": LoadType.LIGHT_DYNAMIC},
            "effects": {"requirements.min_tensile_strength": StrengthLevel.MODERATE},
        },
        {
            "id": "high_strength",
            "conditions": {"load.vibration": True},
            "effects": {"requirements.min_tensile_strength": StrengthLevel.HIGH},
        },
    ]

    task = make_empty_task()
    task.load.load_type = LoadType.LIGHT_DYNAMIC
    task.load.vibration = True

    engine = ForwardChainingEngine(RuleFactory(specs).build_rule_base())
    engine.infer(task)

    assert task.requirements.min_tensile_strength is StrengthLevel.HIGH


def test_action_does_not_weaken_existing_requirement():
    specs = [
        {
            "id": "high_strength",
            "conditions": {"load.vibration": True},
            "effects": {"requirements.min_tensile_strength": StrengthLevel.HIGH},
        },
        {
            "id": "low_strength",
            "conditions": {"load.load_type": LoadType.STATIC},
            "effects": {"requirements.min_tensile_strength": StrengthLevel.LOW},
        },
    ]

    task = make_empty_task()
    task.load.vibration = True

    engine = ForwardChainingEngine(RuleFactory(specs).build_rule_base())
    engine.infer(task)

    assert task.requirements.min_tensile_strength is StrengthLevel.HIGH


def test_rule_fires_only_once():
    specs = [
        {
            "id": "single_fire",
            "conditions": {"environment.moisture": MoistureExposure.NONE},
            "effects": {"requirements.min_water_resistance": ResistanceLevel.FAIR},
        }
    ]

    task = make_empty_task()

    engine = ForwardChainingEngine(RuleFactory(specs).build_rule_base())
    engine.infer(task)
    engine.infer(task)

    assert engine.fired_rules == {"single_fire"}


def test_rule_isolation_independent_effects():
    specs = [
        {
            "id": "water_rule",
            "conditions": {"environment.moisture": MoistureExposure.OUTDOOR},
            "effects": {"requirements.min_water_resistance": ResistanceLevel.GOOD},
        },
        {
            "id": "chemical_rule",
            "conditions": {"environment.chemical_exposure": True},
            "effects": {
                "requirements.min_chemical_resistance": ResistanceLevel.EXCELLENT
            },
        },
    ]

    task = make_empty_task()
    task.environment.moisture = MoistureExposure.OUTDOOR
    task.environment.chemical_exposure = True

    engine = ForwardChainingEngine(RuleFactory(specs).build_rule_base())
    engine.infer(task)

    assert task.requirements.min_water_resistance is ResistanceLevel.GOOD
    assert task.requirements.min_chemical_resistance is ResistanceLevel.EXCELLENT
