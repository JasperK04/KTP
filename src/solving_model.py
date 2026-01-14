"""
Problem-Solving Model for the Fastener Recommendation Knowledge System.

This module implements the Problem-Solving Model as defined in the Knowledge
Technology Practical (KTP). The problem-solving model describes *how* the system
solves a problem in terms of conceptual stages, independently of the domain
knowledge and inference rules.

The model structures the solution process into clearly defined phases:
1. Problem specification
2. Requirement derivation
3. Candidate evaluation
4. Recommendation

This module does not contain domain knowledge or rules. Instead, it coordinates
the interaction between the domain model and the rule model.
"""

from domain_model import Fastener, FasteningTask
from rule_model import ForwardChainingEngine


class ProblemSolvingModel:
    """
    Encapsulates the problem-solving process for a fastening task.

    This class defines the sequence of conceptual steps the system follows
    to arrive at a fastening recommendation. It acts as the control structure
    that connects user input, inference, and final output.
    """

    def __init__(
        self,
        rule_engine: ForwardChainingEngine,
        fasteners: list[Fastener],
    ):
        """
        Initialize the problem-solving model.

        :param rule_engine: Forward-chaining inference engine.
        :param fasteners: List of candidate fasteners.
        """
        self.rule_engine = rule_engine
        self.fasteners = fasteners

    # ─────────────────────────────────────────────
    # PHASE 1: PROBLEM SPECIFICATION
    # ─────────────────────────────────────────────

    def specify_problem(self, task: FasteningTask) -> None:
        """
        Specify the fastening problem.

        In this phase, the FasteningTask is assumed to be populated with
        initial information, such as materials, environment, load conditions,
        and usage constraints. No inference is performed here.

        This method exists to make the phase explicit in the problem-solving
        model.
        """
        pass

    # ─────────────────────────────────────────────
    # PHASE 2: REQUIREMENT DERIVATION
    # ─────────────────────────────────────────────

    def derive_requirements(self, task: FasteningTask) -> None:
        """
        Derive fastening requirements using inference.

        In this phase, the forward-chaining rule engine is applied to the
        fastening task. Rules inspect the task state and add or refine
        derived requirements.
        """
        self.rule_engine.infer(task)

    # ─────────────────────────────────────────────
    # PHASE 3: CANDIDATE EVALUATION
    # ─────────────────────────────────────────────

    def evaluate_candidates(self, task: FasteningTask) -> list[Fastener]:
        """
        Evaluate candidate fasteners against derived requirements.

        This phase filters the available fasteners based on whether they
        satisfy the requirements inferred in the previous phase.

        :param task: The fastening task containing derived requirements.
        :return: List of fasteners that satisfy all requirements.
        """
        suitable_fasteners = []

        for fastener in self.fasteners:
            if self._fastener_satisfies_requirements(fastener, task):
                suitable_fasteners.append(fastener)

        return suitable_fasteners

    def _fastener_satisfies_requirements(
        self, fastener: Fastener, task: FasteningTask
    ) -> bool:
        req = task.requirements

        # Category constraints
        if req.allowed_categories and fastener.category not in req.allowed_categories:
            return False
        if fastener.category in req.excluded_categories:
            return False

        # Rigidity constraints
        if req.allowed_rigidities and fastener.rigidity not in req.allowed_rigidities:
            return False

        # Strength constraints
        if fastener.tensile_strength.value < req.min_tensile_strength.value:
            return False
        if fastener.shear_strength.value < req.min_shear_strength.value:
            return False

        # Resistance constraints
        if fastener.water_resistance.value < req.min_water_resistance.value:
            return False
        if fastener.temperature_resistance.value < req.min_temperature_resistance.value:
            return False
        if fastener.uv_resistance.value < req.min_uv_resistance.value:
            return False
        if fastener.vibration_resistance.value < req.min_vibration_resistance.value:
            return False
        if fastener.chemical_resistance.value < req.min_chemical_resistance.value:
            return False

        # One-sided access constraint
        if task.constraints.one_side_accessable and fastener.requires_two_sided_access:
            return False

        return True

    # ─────────────────────────────────────────────
    # PHASE 4: RECOMMENDATION
    # ─────────────────────────────────────────────

    def recommend(self, task: FasteningTask) -> list[Fastener]:
        """
        Execute the full problem-solving process and return recommendations.

        This method represents the complete problem-solving model by executing
        all phases in sequence.

        :param task: The fastening task to solve.
        :return: List of recommended fasteners.
        """
        self.specify_problem(task)
        self.derive_requirements(task)
        return self.evaluate_candidates(task)
