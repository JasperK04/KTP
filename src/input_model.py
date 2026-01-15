"""
Input Model for the Fastener Recommendation Knowledge System.

This module manages user input in a UI-agnostic way. It loads questions
from the knowledge base, selects the next best question to ask, stores
answers, and incrementally populates a FasteningTask.

The input model acts as an API that can be used by multiple frontends
(e.g., CLI, Flask).
"""

from typing import Any

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
    StrengthLevel,
    UsageConstraints,
)


class InputModel:
    """
    API-style input model that manages question asking and answer storage.
    """

    def __init__(
        self, questions: list[dict[str, Any]], materials: list[dict[str, Any]]
    ):
        """
        Initialize the input model.

        :param questions: List of question specifications from the KB.
        """
        self.questions = questions
        self.materials: dict[str, dict[str, Any]] = {
            mat["material_type"]: mat for mat in materials
        }
        self.answers: dict[str, Any] = {}

        self.task = self._create_empty_task()

    # ─────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────

    def get_state(self) -> dict[str, Any]:
        """
        Serialize the input model state to a dictionary.

        :return: A dictionary representation of the input model state.
        """
        return {
            "answers": self.answers,
        }

    def restore_state(self, state: dict[str, Any]) -> None:
        """
        Restore the input model state from a dictionary.

        :param state: A dictionary representation of the input model state.
        """
        self.answers = state.get("answers", {})
        for question_id, value in self.answers.items():
            question = self._get_question(question_id)
            self._apply_answer(question["attribute"], value)

    def is_question_applicable(self, question: dict) -> bool:
        """
        Determine whether a question is applicable given current answers.

        A question is applicable if:
        - it has no 'ask_if' condition, or
        - all 'ask_if' conditions are satisfied by current task state
        """
        ask_if = question.get("ask_if")
        if not ask_if:
            return True

        for path, expected in ask_if.items():
            try:
                value = self._resolve_path(self.task, path)
            except AttributeError:
                return False

            if isinstance(expected, list):
                if value not in expected:
                    return False
            else:
                if value != expected:
                    return False

        return True

    def get_next_question(self):
        """
        Return the next applicable, unanswered question.
        """
        for question in self.questions:
            if question["id"] in self.answers:
                continue

            if not self.is_question_applicable(question):
                continue

            return question

        return None

    def answer_question(self, question_id: str, value: Any) -> None:
        """
        Store an answer and update the domain model accordingly.

        :param question_id: Identifier of the answered question.
        :param value: Answer value.
        """
        question = self._get_question(question_id)
        self.answers[question_id] = value
        self._apply_answer(question["attribute"], value)

    def get_task(self) -> FasteningTask:
        """
        Return the current FasteningTask populated with all given answers.

        :return: FasteningTask instance.
        """
        return self.task

    def get_question_explanation(self, question_id: str) -> list[str]:
        """
        Return a human-readable explanation of why a question is asked.
        """
        question = self._get_question(question_id)
        rules = question.get("helps_rules", [])

        if not rules:
            return ["This question helps specify the fastening task."]

        return rules

    # ─────────────────────────────────────────────
    # INTERNAL METHODS
    # ─────────────────────────────────────────────

    def _resolve_path(self, obj, path: str):
        for part in path.split("."):
            obj = getattr(obj, part)
        return obj

    def _get_question(self, question_id: str) -> dict[str, Any]:
        for q in self.questions:
            if q["id"] == question_id:
                return q
        raise ValueError(f"Unknown question id: {question_id}")

    def _apply_answer(self, attribute_path: str, value: Any) -> None:
        """
        Apply an answer value to the FasteningTask using an attribute path.

        :param attribute_path: Dotted path (e.g., 'environment.moisture').
        :param value: Answer value.
        """
        target, attr = self._resolve_parent(self.task, attribute_path)
        if attribute_path.endswith("material_type"):
            self._apply_material(target, value)

        setattr(target, attr, self._coerce_value(attr, value))

    def _apply_material(self, material_obj: Material, material_type: str):
        spec = self.materials[material_type]

        material_obj.material_type = MaterialType(material_type)
        material_obj.porosity = spec["porosity"]
        material_obj.brittleness = spec["brittleness"]
        material_obj.base_strength = StrengthLevel(spec["base_strength"])

    def _resolve_parent(self, obj: Any, path: str):
        parts = path.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        return obj, parts[-1]

    def _coerce_value(self, attr: str, value: Any) -> Any:
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            if value.lower() == "false":
                return False

        enum_map = {
            "material_type": MaterialType,
            "moisture": MoistureExposure,
            "load_type": LoadType,
            "permanence": Permanence,
        }

        if attr in enum_map:
            return enum_map[attr](value)

        return value

    def _create_empty_task(self) -> FasteningTask:
        """
        Create an empty FasteningTask with placeholder sub-objects.
        """
        material_placeholder = Material(
            material_type=None,  # pyright: ignore[reportArgumentType]
            porosity="none",
            brittleness="none",
            base_strength=None,  # pyright: ignore[reportArgumentType]
        )

        return FasteningTask(
            materials=MaterialPair(material_placeholder, material_placeholder),
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
