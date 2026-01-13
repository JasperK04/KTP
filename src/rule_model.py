"""
Rule Model for the Fastener Recommendation Knowledge System.

This module implements the Rule Model as defined in the Knowledge Technology
Practical (KTP). It contains declarative IF–THEN rules that operate on domain
objects and perform inference using forward chaining.

The rules themselves are not hardcoded in this module. Instead, they are
generated automatically from a declarative rule specification stored in the
knowledge base (kb.json). This ensures a strict separation between:

- Domain knowledge (stored in the KB)
- Rule representation (this module)
- Inference control (forward chaining)

This design follows the KTP requirement that knowledge must be modular,
explicit, expert-verifiable, and independent from the inference mechanism.
"""

from dataclasses import dataclass
from typing import Any, Callable

from domain_model import FasteningTask, Rigidity, StrengthLevel


@dataclass
class Rule:
    """
    Represents a single declarative IF–THEN rule.

    A rule consists of:
    - a condition: a predicate over a FasteningTask (the IF-part)
    - an action: a state-modifying operation on a FasteningTask (the THEN-part)

    Rules do not return values. When fired, they add or refine knowledge by
    updating attributes of domain objects.
    """

    id: str
    condition: Callable[[FasteningTask], bool]
    action: Callable[[FasteningTask], None]


class RuleBase:
    """
    Container for a set of rules.

    The RuleBase represents the complete rule model of the system.
    It contains no inference logic and no domain knowledge beyond
    the rules themselves.
    """

    def __init__(self, rules: list[Rule]):
        """
        Initialize the rule base.

        :param rules: A list of Rule objects.
        """
        self.rules = rules


class ForwardChainingEngine:
    """
    Forward-chaining inference engine.

    This engine applies rules in a data-driven manner: rules are repeatedly
    evaluated against the current state of a FasteningTask until no new
    information can be derived.

    Each rule is fired at most once.
    """

    def __init__(self, rule_base: RuleBase):
        """
        Initialize the inference engine.

        :param rule_base: The RuleBase containing all rules.
        """
        self.rule_base = rule_base
        self.fired_rules: set[str] = set()

    def infer(self, task: FasteningTask) -> None:
        """
        Perform forward-chaining inference on a fastening task.

        Rules whose conditions are satisfied are applied, potentially modifying
        the task. Inference continues until no additional rules can be fired.

        :param task: The FasteningTask being reasoned about.
        """
        changed = True

        while changed:
            changed = False

            for rule in self.rule_base.rules:
                if rule.id in self.fired_rules:
                    continue

                if rule.condition(task):
                    rule.action(task)
                    self.fired_rules.add(rule.id)
                    changed = True


class RuleFactory:
    """
    Factory for generating executable rules from declarative rule specifications.

    This class translates rule descriptions from the knowledge base into Rule
    objects consisting of executable conditions and actions. It enables the
    system to remain fully data-driven: modifying rules in the KB does not
    require changes to code.
    """

    def __init__(self, rule_specs: list[dict[str, Any]]):
        """
        Initialize the rule factory.

        :param rule_specs: A list of rule specifications as loaded from kb.json.
        """
        self.rule_specs = rule_specs

    def build_rule_base(self) -> RuleBase:
        """
        Build a RuleBase from the rule specifications.

        :return: A RuleBase containing executable Rule objects.
        """
        rules = [self._build_rule(spec) for spec in self.rule_specs]
        return RuleBase(rules)

    def _build_rule(self, spec: dict[str, Any]) -> Rule:
        """
        Construct a single Rule from its specification.

        :param spec: A dictionary describing one rule.
        :return: A Rule object.
        """
        rule_id = spec["id"]
        condition_spec = spec["conditions"]
        effect_spec = spec["effects"]

        condition = self._build_condition(condition_spec)
        action = self._build_action(effect_spec)

        return Rule(rule_id, condition, action)

    def _build_condition(
        self, condition_spec: dict[str, Any]
    ) -> Callable[[FasteningTask], bool]:
        """
        Build a condition function from a declarative condition specification.

        The condition evaluates to True if all specified attribute paths match
        their expected values.

        :param condition_spec: Mapping from attribute paths to expected values.
        :return: A predicate over FasteningTask.
        """

        def condition(task: FasteningTask) -> bool:
            for path, expected in condition_spec.items():
                value = self._resolve_path(task, path)

                if callable(value):
                    value = value()

                if isinstance(value, list):
                    if expected not in value:
                        return False
                else:
                    if value != expected:
                        return False

            return True

        return condition

    def _build_action(
        self, effect_spec: dict[str, Any]
    ) -> Callable[[FasteningTask], None]:
        """
        Build an action function from a declarative effect specification.

        The action modifies attributes of a FasteningTask or its sub-objects,
        adding or refining derived knowledge.

        :param effect_spec: Mapping from attribute paths to values to assign.
        :return: An action function operating on FasteningTask.
        """

        def action(task: FasteningTask) -> None:
            for path, value in effect_spec.items():
                target, attr = self._resolve_parent(task, path)

                if isinstance(value, list):
                    current = getattr(target, attr)
                    if isinstance(current, set):
                        current.update(self._coerce_values(value))
                    else:
                        setattr(target, attr, value)
                else:
                    setattr(target, attr, self._coerce_value(value))

        return action

    def _resolve_any(self, obj, remaining_path):
        """
        Resolve an 'any' quantifier over a MaterialPair.

        :param obj: Object on which 'any' is applied (e.g., MaterialPair).
        :param remaining_path: Attribute path to evaluate on each element.
        :return: List of resolved values.
        """
        values = []

        for attr_name in ("material_a", "material_b"):
            if hasattr(obj, attr_name):
                sub_obj = getattr(obj, attr_name)
                values.append(self._resolve_path(sub_obj, remaining_path))

        return values

    def _resolve_path(self, obj, path: str):
        """
        Resolve a dotted attribute path, supporting the 'any' quantifier.
        """
        parts = path.split(".")

        i = 0
        while i < len(parts):
            part = parts[i]

            if part == "any":
                remaining_path = ".".join(parts[i + 1 :])
                return self._resolve_any(obj, remaining_path)

            if not hasattr(obj, part):
                raise AttributeError(
                    f"Invalid rule path '{path}': "
                    f"'{type(obj).__name__}' has no attribute '{part}'"
                )

            obj = getattr(obj, part)
            i += 1

        return obj

    def _resolve_parent(self, obj: Any, path: str):
        """
        Resolve the parent object and attribute name for a dotted path.

        :param obj: Root object.
        :param path: Dotted attribute path.
        :return: Tuple (parent_object, attribute_name).
        """
        parts = path.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        return obj, parts[-1]

    def _coerce_value(self, value: Any) -> Any:
        """
        Convert string values to Enum members where applicable.

        Uses only public Enum APIs. If the value does not correspond to a known
        Enum member, it is returned unchanged.

        :param value: Value to coerce.
        :return: Coerced value or original value.
        """
        for enum_cls in (StrengthLevel, Rigidity):
            try:
                return enum_cls(value)
            except ValueError:
                pass
        return value

    def _coerce_values(self, values: list[Any]) -> set[Any]:
        """
        Coerce a list of values into a set, converting Enum values where possible.

        :param values: List of values from the KB.
        :return: Set of coerced values.
        """
        return {self._coerce_value(v) for v in values}
