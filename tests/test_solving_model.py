import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add source directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
from src.rule_model import ForwardChainingEngine
from src.solving_model import ProblemSolvingModel

# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────


@pytest.fixture
def mock_rule_engine():
    """Creates a mock inference engine."""
    engine = MagicMock(spec=ForwardChainingEngine)
    engine.infer = MagicMock()
    return engine


@pytest.fixture
def standard_fastener():
    """Creates a 'standard' fastener with known properties for testing."""
    return Fastener(
        name="Test Bolt",
        category="mechanical",
        compatible_materials=[MaterialType.METAL],
        tensile_strength=StrengthLevel.MODERATE,
        shear_strength=StrengthLevel.MODERATE,
        water_resistance=ResistanceLevel.FAIR,
        temperature_resistance=ResistanceLevel.FAIR,
        uv_resistance=ResistanceLevel.FAIR,
        vibration_resistance=ResistanceLevel.FAIR,
        chemical_resistance=ResistanceLevel.FAIR,
        rigidity=Rigidity.RIGID,
        permanence=Permanence.REMOVABLE,
        requires_two_sided_access=False,
    )


@pytest.fixture
def empty_task():
    """Creates a basic task with empty requirements."""
    mat = Material(MaterialType.METAL, "low", "low", StrengthLevel.HIGH)
    return FasteningTask(
        materials=MaterialPair(mat, mat),
        environment=Environment(MoistureExposure.NONE, False, False, False),
        load=LoadCondition(LoadType.STATIC, False, False, False),
        constraints=UsageConstraints(
            Permanence.REMOVABLE, False, False, False, False, False, None
        ),
        requirements=DerivedRequirements(),
    )


@pytest.fixture
def solver(mock_rule_engine, standard_fastener):
    """Creates the ProblemSolvingModel with the mock engine and one fastener."""
    return ProblemSolvingModel(mock_rule_engine, [standard_fastener])


# ─────────────────────────────────────────────
# 1. CANDIDATE FILTERING
# ─────────────────────────────────────────────


class TestCandidateFiltering:
    def test_category_filtering(self, solver, empty_task, standard_fastener):
        """Test that fasteners are filtered by allowed/excluded categories."""
        # Case 1: Category allowed -> Pass
        empty_task.requirements.allowed_categories = {"mechanical"}
        assert solver.evaluate_candidates(empty_task) == [standard_fastener]

        # Case 2: Category mismatch -> Fail
        empty_task.requirements.allowed_categories = {"adhesive"}
        assert solver.evaluate_candidates(empty_task) == []

        # Case 3: Category excluded -> Fail
        empty_task.requirements.allowed_categories = set()
        empty_task.requirements.excluded_categories = {"mechanical"}
        assert solver.evaluate_candidates(empty_task) == []

    def test_rigidity_filtering(self, solver, empty_task, standard_fastener):
        """Test filtering by rigidity (e.g. Flexible vs Rigid)."""
        # Fastener is RIGID

        # Case 1: Allowed Rigidities includes Rigid -> Pass
        empty_task.requirements.allowed_rigidities = {Rigidity.RIGID}
        assert solver.evaluate_candidates(empty_task) == [standard_fastener]

        # Case 2: Allowed Rigidities only Flexible -> Fail
        empty_task.requirements.allowed_rigidities = {Rigidity.FLEXIBLE}
        assert solver.evaluate_candidates(empty_task) == []

    def test_strength_filtering(self, solver, empty_task, standard_fastener):
        """Test filtering by ordinal strength thresholds."""
        # Fastener is MODERATE strength

        # Case 1: Requirement is LOWER than fastener (Low) -> Pass
        empty_task.requirements.min_tensile_strength = StrengthLevel.LOW
        assert solver.evaluate_candidates(empty_task) == [standard_fastener]

        # Case 2: Requirement is EQUAL to fastener (Moderate) -> Pass
        empty_task.requirements.min_tensile_strength = StrengthLevel.MODERATE
        assert solver.evaluate_candidates(empty_task) == [standard_fastener]

        # Case 3: Requirement is HIGHER than fastener (High) -> Fail
        empty_task.requirements.min_tensile_strength = StrengthLevel.HIGH
        assert solver.evaluate_candidates(empty_task) == []

    def test_resistance_filtering(self, solver, empty_task, standard_fastener):
        """Test filtering by various resistance types."""
        # Fastener has FAIR resistance across the board

        # Test Water Resistance
        empty_task.requirements.min_water_resistance = ResistanceLevel.GOOD
        assert solver.evaluate_candidates(empty_task) == []

        empty_task.requirements.min_water_resistance = ResistanceLevel.POOR
        assert solver.evaluate_candidates(empty_task) == [standard_fastener]

        # Test Chemical Resistance (Independent check)
        empty_task.requirements.min_water_resistance = ResistanceLevel.NONE
        empty_task.requirements.min_chemical_resistance = ResistanceLevel.EXCELLENT
        assert solver.evaluate_candidates(empty_task) == []


# ─────────────────────────────────────────────
# 2. ACCESS CONSTRAINTS
# ─────────────────────────────────────────────


class TestAccessConstraints:
    def test_one_sided_access_constraint(self, mock_rule_engine, empty_task):
        """Test that one-sided access excludes fasteners requiring two sides."""

        # Setup two fasteners: one needs 2 sides (Bolt), one needs 1 side (Screw)
        bolt = Fastener(
            name="Bolt",
            category="mechanical",
            compatible_materials=[MaterialType.METAL],
            tensile_strength=StrengthLevel.MODERATE,
            shear_strength=StrengthLevel.MODERATE,
            water_resistance=ResistanceLevel.FAIR,
            temperature_resistance=ResistanceLevel.FAIR,
            uv_resistance=ResistanceLevel.FAIR,
            vibration_resistance=ResistanceLevel.FAIR,
            chemical_resistance=ResistanceLevel.FAIR,
            rigidity=Rigidity.RIGID,
            permanence=Permanence.REMOVABLE,
            requires_two_sided_access=True,
        )
        screw = Fastener(
            name="Screw",
            category="mechanical",
            compatible_materials=[MaterialType.METAL],
            tensile_strength=StrengthLevel.MODERATE,
            shear_strength=StrengthLevel.MODERATE,
            water_resistance=ResistanceLevel.FAIR,
            temperature_resistance=ResistanceLevel.FAIR,
            uv_resistance=ResistanceLevel.FAIR,
            vibration_resistance=ResistanceLevel.FAIR,
            chemical_resistance=ResistanceLevel.FAIR,
            rigidity=Rigidity.RIGID,
            permanence=Permanence.REMOVABLE,
            requires_two_sided_access=False,
        )

        solver = ProblemSolvingModel(mock_rule_engine, [bolt, screw])

        # Scenario: User only has access to ONE side
        empty_task.constraints.one_side_accessable = True

        results = solver.evaluate_candidates(empty_task)

        # Should only contain the screw, not the bolt
        assert len(results) == 1
        assert results[0].name == "Screw"

    def test_two_sided_access_available(self, mock_rule_engine, empty_task):
        """Test that having two-sided access allows all fasteners."""

        bolt = Fastener(
            name="Bolt",
            category="mechanical",
            compatible_materials=[MaterialType.METAL],
            tensile_strength=StrengthLevel.MODERATE,
            shear_strength=StrengthLevel.MODERATE,
            water_resistance=ResistanceLevel.FAIR,
            temperature_resistance=ResistanceLevel.FAIR,
            uv_resistance=ResistanceLevel.FAIR,
            vibration_resistance=ResistanceLevel.FAIR,
            chemical_resistance=ResistanceLevel.FAIR,
            rigidity=Rigidity.RIGID,
            permanence=Permanence.REMOVABLE,
            requires_two_sided_access=True,
        )

        solver = ProblemSolvingModel(mock_rule_engine, [bolt])

        # Scenario: User has access to BOTH sides (one_side_accessable = False)
        empty_task.constraints.one_side_accessable = False

        results = solver.evaluate_candidates(empty_task)
        assert len(results) == 1
        assert results[0].name == "Bolt"


# ─────────────────────────────────────────────
# 3. FULL PIPELINE
# ─────────────────────────────────────────────


class TestFullPipeline:
    def test_recommend_method_flow(self, solver, empty_task, mock_rule_engine):
        """
        Tests the full 'recommend' pipeline:
        Specify -> Derive (via Mock Engine) -> Evaluate -> Output
        """

        # 1. Setup the behavior of the mock engine.
        def simulate_inference(task):
            # Simulate a rule saying: "We need High Strength"
            task.requirements.min_tensile_strength = StrengthLevel.HIGH

        mock_rule_engine.infer.side_effect = simulate_inference

        # 2. Run the full pipeline
        results = solver.recommend(empty_task)

        # 3. Assertions
        mock_rule_engine.infer.assert_called_once_with(empty_task)

        # Verify the candidate was filtered out based on the inferred requirement
        assert len(results) == 0

    def test_recommend_success_flow(self, solver, empty_task, mock_rule_engine):
        """Tests a successful run of the pipeline."""

        def simulate_inference(task):
            # Simulate a rule setting a requirement the fastener CAN meet
            task.requirements.min_tensile_strength = StrengthLevel.LOW

        mock_rule_engine.infer.side_effect = simulate_inference

        results = solver.recommend(empty_task)

        mock_rule_engine.infer.assert_called_once()
        assert len(results) == 1
        assert results[0].name == "Test Bolt"
