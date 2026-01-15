import pytest

from src.domain_model import (
    DerivedRequirements,
    Environment,
    Fastener,
    FasteningTask,
    LoadCondition,
    LoadType,
    Material,
    MaterialPair,
    MaterialType,
    MoistureExposure,
    Permanence,
    ResistanceLevel,
    Rigidity,
    StrengthLevel,
    UsageConstraints,
)

# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────


def test_enum_values_are_strings():
    assert MaterialType.WOOD.value == "wood"
    assert MoistureExposure.SUBMERGED.value == "submerged"
    assert LoadType.HEAVY_DYNAMIC.value == "heavy_dynamic"
    assert Permanence.PERMANENT.value == "permanent"
    assert Rigidity.RIGID.value == "rigid"
    assert StrengthLevel.VERY_HIGH.value == "very_high"
    assert ResistanceLevel.EXCELLENT.value == "excellent"


def test_enum_construction_from_value():
    assert MaterialType("metal") is MaterialType.METAL
    assert StrengthLevel("high") is StrengthLevel.HIGH
    assert ResistanceLevel("good") is ResistanceLevel.GOOD


# ─────────────────────────────────────────────
# MATERIAL
# ─────────────────────────────────────────────
def test_material_to_from_dict_roundtrip():
    material = Material(
        material_type=MaterialType.METAL,
        porosity="low",
        brittleness="low",
        base_strength=StrengthLevel.HIGH,
    )

    data = material.to_dict()
    restored = Material.from_dict(data)

    assert restored == material
    assert restored.material_type is MaterialType.METAL
    assert restored.base_strength is StrengthLevel.HIGH


# ─────────────────────────────────────────────
# MATERIAL PAIR
# ─────────────────────────────────────────────
def test_material_pair_same_material_true():
    m = Material(
        material_type=MaterialType.WOOD,
        porosity="medium",
        brittleness="medium",
        base_strength=StrengthLevel.MODERATE,
    )

    pair = MaterialPair(m, m)
    assert pair.same_material() is True


def test_material_pair_same_material_false():
    m1 = Material(
        material_type=MaterialType.WOOD,
        porosity="medium",
        brittleness="medium",
        base_strength=StrengthLevel.MODERATE,
    )
    m2 = Material(
        material_type=MaterialType.METAL,
        porosity="low",
        brittleness="low",
        base_strength=StrengthLevel.HIGH,
    )

    pair = MaterialPair(m1, m2)
    assert pair.same_material() is False


def test_material_pair_to_from_dict_roundtrip():
    pair = MaterialPair(
        Material(
            material_type=MaterialType.PLASTIC,
            porosity="low",
            brittleness="low",
            base_strength=StrengthLevel.LOW,
        ),
        Material(
            material_type=MaterialType.METAL,
            porosity="none",
            brittleness="low",
            base_strength=StrengthLevel.HIGH,
        ),
    )

    restored = MaterialPair.from_dict(pair.to_dict())
    assert restored == pair


# ─────────────────────────────────────────────
# ENVIRONMENT
# ─────────────────────────────────────────────
def test_environment_to_from_dict_roundtrip():
    env = Environment(
        moisture=MoistureExposure.OUTDOOR,
        chemical_exposure=True,
        uv_exposure=True,
        temperature_extremes=False,
    )

    restored = Environment.from_dict(env.to_dict())
    assert restored == env
    assert restored.moisture is MoistureExposure.OUTDOOR


# ─────────────────────────────────────────────
# LOAD CONDITION
# ─────────────────────────────────────────────
def test_load_condition_with_required_strength():
    load = LoadCondition(
        load_type=LoadType.HEAVY_DYNAMIC,
        vibration=True,
        tension_dominant=True,
        shock_loads=True,
        required_strength=StrengthLevel.VERY_HIGH,
    )

    restored = LoadCondition.from_dict(load.to_dict())
    assert restored == load
    assert restored.required_strength is StrengthLevel.VERY_HIGH


def test_load_condition_without_required_strength():
    load = LoadCondition(
        load_type=LoadType.STATIC,
        vibration=False,
        tension_dominant=False,
        shock_loads=False,
        required_strength=None,
    )

    restored = LoadCondition.from_dict(load.to_dict())
    assert restored.required_strength is None


# ─────────────────────────────────────────────
# USAGE CONSTRAINTS
# ─────────────────────────────────────────────
def test_usage_constraints_to_from_dict_roundtrip():
    constraints = UsageConstraints(
        permanence=Permanence.REMOVABLE,
        flexibility_required=True,
        orientation_vertical=True,
        precision_required=False,
        health_constraints=True,
        one_side_accessable=True,
        max_curing_time="fast",
    )

    restored = UsageConstraints.from_dict(constraints.to_dict())
    assert restored == constraints
    assert restored.permanence is Permanence.REMOVABLE


# ─────────────────────────────────────────────
# DERIVED REQUIREMENTS
# ─────────────────────────────────────────────
def test_derived_requirements_defaults():
    req = DerivedRequirements()

    assert req.min_tensile_strength is StrengthLevel.NONE
    assert req.allowed_categories == set()
    assert req.excluded_categories == set()


def test_derived_requirements_to_from_dict_roundtrip():
    req = DerivedRequirements(
        min_tensile_strength=StrengthLevel.HIGH,
        min_shear_strength=StrengthLevel.MODERATE,
        min_water_resistance=ResistanceLevel.GOOD,
        allowed_rigidities={Rigidity.RIGID},
        allowed_categories={"adhesive"},
        excluded_categories={"nail"},
    )

    restored = DerivedRequirements.from_dict(req.to_dict())
    assert restored == req
    assert Rigidity.RIGID in restored.allowed_rigidities


# ─────────────────────────────────────────────
# FASTENING TASK
# ─────────────────────────────────────────────
def test_fastening_task_to_from_dict_roundtrip():
    task = FasteningTask(
        materials=MaterialPair(
            Material(
                material_type=MaterialType.WOOD,
                porosity="medium",
                brittleness="medium",
                base_strength=StrengthLevel.MODERATE,
            ),
            Material(
                material_type=MaterialType.WOOD,
                porosity="medium",
                brittleness="medium",
                base_strength=StrengthLevel.MODERATE,
            ),
        ),
        environment=Environment(
            moisture=MoistureExposure.SPLASH,
            chemical_exposure=False,
            uv_exposure=False,
            temperature_extremes=False,
        ),
        load=LoadCondition(
            load_type=LoadType.LIGHT_DYNAMIC,
            vibration=True,
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

    restored = FasteningTask.from_dict(task.to_dict())
    assert restored == task


# ─────────────────────────────────────────────
# FASTENER
# ─────────────────────────────────────────────
def test_fastener_to_from_dict_roundtrip():
    fastener = Fastener(
        name="Test Bolt",
        category="bolt",
        compatible_materials=[MaterialType.METAL],
        tensile_strength=StrengthLevel.VERY_HIGH,
        shear_strength=StrengthLevel.HIGH,
        water_resistance=ResistanceLevel.GOOD,
        temperature_resistance=ResistanceLevel.EXCELLENT,
        uv_resistance=ResistanceLevel.GOOD,
        vibration_resistance=ResistanceLevel.GOOD,
        chemical_resistance=ResistanceLevel.FAIR,
        rigidity=Rigidity.RIGID,
        permanence=Permanence.PERMANENT,
        requires_two_sided_access=True,
    )

    restored = Fastener.from_dict(fastener.to_dict())
    assert restored == fastener
    assert restored.compatible_materials == [MaterialType.METAL]
