import json
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum

# -----------------------------------------------
# ENUM classes
# -----------------------------------------------


class Strength(Enum):
    NONE = "none"
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Resistance(Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class Permanence(Enum):
    REMOVABLE = "removable"
    SEMI_PERMANENT = "semi_permanent"
    PERMANENT = "permanent"


class Rigidity(Enum):
    FLEXIBLE = "flexible"
    SEMI_FLEXIBLE = "semi_flexible"
    RIGID = "rigid"


class FastenerCategory(Enum):
    ADHESIVE = "adhesive"
    MECHANICAL = "mechanical"
    THERMAL = "thermal"


class QuestionType(Enum):
    CHOICE = "choice"
    BOOLEAN = "boolean"


# -----------------------------------------------
# Ordinal scales
# -----------------------------------------------


class OrdinalScales:
    """Centralized ordinal scales for comparisons"""

    STRENGTH = ["none", "very_low", "low", "moderate", "high", "very_high"]
    RESISTANCE = ["poor", "fair", "good", "excellent"]

    # Mapping of exposure types to minimum required resistance
    MOISTURE_TO_RESISTANCE = {
        "no": "poor",
        "splash": "fair",
        "outdoor": "good",
        "submerged": "excellent",
    }


# -----------------------------------------------
# Dataclasses
# -----------------------------------------------


@dataclass
class Question:
    """Represents a question to the user."""

    id: str
    text: str
    type: QuestionType
    choices: list[str] = field(default_factory=list)
    applicable_to: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "answer_type": self.type.value,
            "choices": self.choices,
            "applicable_to": self.applicable_to,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        return cls(
            id=data["id"],
            text=data["text"],
            type=QuestionType(data["answer_type"]),
            choices=data.get("choices", []) if data.get("choices") is not None else [],
            applicable_to=data.get("applicable_to", []),
        )


@dataclass
class Rule:
    """Represents an inference rule"""

    id: str
    conditions: dict[str, any]  # question_id -> expected_value
    conclusion: dict[str, any]  # attribute -> value pairs
    priority: int = 0  # Higher priority rules are evaluated first

    def to_dict(self) -> dict[str, any]:
        return {
            "id": self.id,
            "conditions": self.conditions,
            "conclusion": self.conclusion,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "Rule":
        return cls(**data)


@dataclass
class SuggestionRule:
    """Represents a contextual suggestion rule"""

    id: str
    applies_to_fasteners: list[str]  # List of fastener names or "all"
    conditions: dict[str, any]  # fact conditions that trigger this suggestion
    suggestion: str  # The suggestion text

    def to_dict(self) -> dict[str, any]:
        return {
            "id": self.id,
            "applies_to_fasteners": self.applies_to_fasteners,
            "conditions": self.conditions,
            "suggestion": self.suggestion,
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "SuggestionRule":
        return cls(**data)


@dataclass
class Fact:
    """Represents a known fact from user answers"""

    question_id: str
    value: any


@dataclass
class MaterialProperties:
    """Properties of a fastener for specific materials"""

    compatible_materials: list[str]
    tensile_strength: Strength
    shear_strength: Strength
    compressive_strength: Strength
    water_resistance: Resistance
    weather_resistance: Resistance
    chemical_resistance: Resistance
    temperature_resistance: Resistance
    vibration_resistance: Resistance
    rigidity: Rigidity
    permanence: Permanence
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, any]:
        return {
            "compatible_materials": self.compatible_materials,
            "tensile_strength": self.tensile_strength.value,
            "shear_strength": self.shear_strength.value,
            "compressive_strength": self.compressive_strength.value,
            "water_resistance": self.water_resistance.value,
            "weather_resistance": self.weather_resistance.value,
            "chemical_resistance": self.chemical_resistance.value,
            "temperature_resistance": self.temperature_resistance.value,
            "vibration_resistance": self.vibration_resistance.value,
            "rigidity": self.rigidity.value,
            "permanence": self.permanence.value,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "MaterialProperties":
        return cls(
            compatible_materials=data["compatible_materials"],
            tensile_strength=Strength(data["tensile_strength"]),
            shear_strength=Strength(data["shear_strength"]),
            compressive_strength=Strength(data["compressive_strength"]),
            water_resistance=Resistance(data["water_resistance"]),
            weather_resistance=Resistance(data["weather_resistance"]),
            chemical_resistance=Resistance(data["chemical_resistance"]),
            temperature_resistance=Resistance(data["temperature_resistance"]),
            vibration_resistance=Resistance(data["vibration_resistance"]),
            rigidity=Rigidity(data["rigidity"]),
            permanence=Permanence(data["permanence"]),
            notes=data.get("notes", []),
        )


@dataclass
class Fastener:
    """Represents a fastening method"""

    name: str
    category: FastenerCategory
    properties: MaterialProperties
    requires_tools: list[str] = field(default_factory=list)
    surface_prep: list[str] = field(default_factory=list)
    curing_time: str | None = None
    special_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, any]:
        return {
            "name": self.name,
            "category": self.category.value,
            "properties": self.properties.to_dict(),
            "requires_tools": self.requires_tools,
            "surface_prep": self.surface_prep,
            "curing_time": self.curing_time,
            "special_conditions": self.special_conditions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "Fastener":
        return cls(
            name=data["name"],
            category=FastenerCategory(data["category"]),
            properties=MaterialProperties.from_dict(data["properties"]),
            requires_tools=data.get("requires_tools", []),
            surface_prep=data.get("surface_prep", []),
            curing_time=data.get("curing_time"),
            special_conditions=data.get("special_conditions", []),
        )


# -----------------------------------------------
# Inference Engine
# -----------------------------------------------


class KnowledgeBase:
    """Stores all fasteners, rules, and questions"""

    def __init__(self):
        self.fasteners: list[Fastener] = []
        self.rules: list[Rule] = []
        self.questions: list[Question] = []
        self.suggestion_rules: list[SuggestionRule] = []

    def load_from_file(self, filepath: str):
        """Load knowledge base from JSON file"""
        with open(filepath, "r") as f:
            data = json.load(f)

        self.questions = [Question.from_dict(q) for q in data.get("questions", [])]
        self.fasteners = [Fastener.from_dict(f) for f in data.get("fasteners", [])]
        self.rules = [Rule.from_dict(r) for r in data.get("rules", [])]
        self.suggestion_rules = [
            SuggestionRule.from_dict(s) for s in data.get("suggestion_rules", [])
        ]

    def save_to_file(self, filepath: str):
        """Save knowledge base to JSON file"""
        data = {
            "questions": [q.to_dict() for q in self.questions],
            "fasteners": [f.to_dict() for f in self.fasteners],
            "rules": [r.to_dict() for r in self.rules],
            "suggestion_rules": [s.to_dict() for s in self.suggestion_rules],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)


class InferenceEngine:
    """Forward-chaining inference engine for fastener selection"""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.facts: dict[str, any] = {}
        self.conclusions: dict[str, any] = {}

    def add_fact(self, question_id: str, value: any):
        """Add a fact from user answer"""
        self.facts[question_id] = value

    def restore_facts(self, facts: dict[str, any]):
        """Restore multiple facts"""
        self.facts.update(facts)

    def retrieve_facts(self) -> any:
        return self.facts

    def reset(self):
        """Clear all facts and conclusions"""
        self.facts.clear()
        self.conclusions.clear()

    def remaining_fasteners(self) -> list[Fastener]:
        return [f for f in self.kb.fasteners if self.matches_fastener(f)]

    def remaining_categories(self, remaining_fasteners):
        return {f.category.value for f in remaining_fasteners}

    def simulate_answer_on_subset(
        self,
        question_id: str,
        value: any,
        subset: list[Fastener],
    ) -> int:
        temp_engine = deepcopy(self)
        temp_engine.add_fact(question_id, value)
        temp_engine.infer()

        return sum(1 for f in subset if temp_engine.matches_fastener(f))

    def question_category_coverage(self, question, remaining_categories) -> int:
        return len(set(question.applicable_to) & remaining_categories)

    def normalized_question_score(self, question) -> float:
        remaining = self.remaining_fasteners()
        n = len(remaining)

        if n <= 1:
            return 0.0

        answers = (
            question.choices if question.type == QuestionType.CHOICE else [True, False]
        )

        remaining_counts = []
        for a in answers:
            remaining_counts.append(
                self.simulate_answer_on_subset(question.id, a, remaining)
            )

        expected_remaining = sum(remaining_counts) / len(answers)

        raw_reduction = n - expected_remaining
        max_reduction = n - (n / len(answers))

        if max_reduction == 0:
            return 0.0

        return raw_reduction / max_reduction

    def is_question_applicable(self, question, remaining_fasteners) -> bool:
        if not question.applicable_to:
            return True

        remaining_categories = {f.category.value for f in remaining_fasteners}

        return bool(remaining_categories & set(question.applicable_to))

    def question_can_discriminate(self, question, remaining_fasteners) -> bool:
        answers = (
            question.choices if question.type == QuestionType.CHOICE else [True, False]
        )

        sizes = set()
        for a in answers:
            count = self.simulate_answer_on_subset(question.id, a, remaining_fasteners)
            sizes.add(count)

        return len(sizes) > 1

    def select_next_question(self, asked_questions: set[str]):
        mandatory = ["material_type", "material_type_2"]

        for qid in mandatory:
            if qid not in self.facts:
                return next(q for q in self.kb.questions if q.id == qid)

        remaining_fasteners = self.remaining_fasteners()
        remaining_categories = self.remaining_categories(remaining_fasteners)

        if len(remaining_fasteners) <= 1:
            return None

        candidates = []

        for question in self.kb.questions:
            if question.id in self.facts or question.id in asked_questions:
                continue

            coverage = self.question_category_coverage(question, remaining_categories)

            if coverage == 0:
                continue

            if not self.question_can_discriminate(question, remaining_fasteners):
                continue

            score = self.normalized_question_score(question)

            candidates.append((question, coverage, score))

        if not candidates:
            return None

        # Step 1: prefer questions covering multiple categories
        max_coverage = max(c[1] for c in candidates)

        # If more than one category remains, prefer multi-category questions
        if len(remaining_categories) > 1:
            multi_category = [c for c in candidates if c[1] > 1]

            if multi_category:
                candidates = multi_category

        # Step 2: select by elimination score
        best_question, _, best_score = max(candidates, key=lambda x: x[2])

        # Step 3: single-category safety check
        if (
            self.question_category_coverage(best_question, remaining_categories) == 1
            and len(remaining_categories) > 1
        ):
            # Only allow if no other question exists
            alternative_exists = any(c for c in candidates if c[1] > 1)
            if alternative_exists:
                return None

        return best_question

    def evaluate_rule(self, rule: Rule) -> bool:
        """Check if a rule's conditions are satisfied"""
        for question_id, expected in rule.conditions.items():
            if question_id not in self.facts:
                return False

            actual = self.facts[question_id]

            # Handle list of acceptable values
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False

        return True

    def apply_rule(self, rule: Rule):
        """Apply a rule's conclusions"""
        for key, value in rule.conclusion.items():
            if key not in self.conclusions:
                self.conclusions[key] = []

            if isinstance(value, list):
                self.conclusions[key].extend(value)
            else:
                self.conclusions[key].append(value)

    def infer(self):
        """Run forward-chaining inference"""
        # NOTE: unsure about the priorioty ranking. Implementing logic anyway.
        # sort by rule priority
        sorted_rules = sorted(self.kb.rules, key=lambda r: r.priority, reverse=True)

        for rule in sorted_rules:
            if self.evaluate_rule(rule):
                self.apply_rule(rule)

    def matches_fastener(self, fastener: Fastener) -> bool:
        """Check if fastener meets all required criteria from facts and conclusions"""

        # Check if fastener category is excluded
        if "exclude_categories" in self.conclusions:
            if fastener.category.value in self.conclusions["exclude_categories"]:
                return False

        # Check if fastener category is recommended (if specified)
        if "recommended_categories" in self.conclusions:
            if (
                fastener.category.value
                not in self.conclusions["recommended_categories"]
            ):
                return False

        # Check required properties from conclusions
        if "required_properties" in self.conclusions:
            for prop_requirement in self.conclusions["required_properties"]:
                # Format: "property_name:required_value"
                if ":" in prop_requirement:
                    prop_name, required_value = prop_requirement.split(":", 1)

                    # Get the property value from fastener
                    if hasattr(fastener.properties, prop_name):
                        actual_value = getattr(fastener.properties, prop_name)

                        # Handle enum values
                        if hasattr(actual_value, "value"):
                            actual_value = actual_value.value

                        if actual_value != required_value:
                            return False

        # Check material compatibility
        if "material_type" in self.facts and "material_type_2" in self.facts:
            material2 = self.facts["material_type_2"]
            # Check for exact match or generic category match
            compatible = False
            compat_materials = fastener.properties.compatible_materials
            if material2 in compat_materials:
                compatible = True

            if not compatible:
                return False

        # Check strength requirements (ordinal comparison)
        if "mechanical_strength" in self.facts:
            required_strength = self.facts["mechanical_strength"]

            req_idx = OrdinalScales.STRENGTH.index(required_strength)
            fastener_idx = OrdinalScales.STRENGTH.index(
                fastener.properties.tensile_strength.value
            )

            if fastener_idx < req_idx:
                return False

        # Check water resistance based on moisture exposure
        if "moisture_exposure" in self.facts:
            exposure = self.facts["moisture_exposure"]

            if exposure in OrdinalScales.MOISTURE_TO_RESISTANCE:
                required_resistance = OrdinalScales.MOISTURE_TO_RESISTANCE[exposure]
                req_idx = OrdinalScales.RESISTANCE.index(required_resistance)
                actual_idx = OrdinalScales.RESISTANCE.index(
                    fastener.properties.water_resistance.value
                )

                if actual_idx < req_idx:
                    return False

        # Check permanence match
        if "permanence" in self.facts:
            required_perm = self.facts["permanence"]
            actual_perm = fastener.properties.permanence.value

            # Exact match or semi-permanent accepts all
            if required_perm == "semi_permanent":
                # Semi-permanent is flexible - any permanence works
                pass
            elif required_perm != actual_perm:
                return False

        # Check flexibility requirement
        if "flexibility" in self.facts:
            needs_flexibility = self.facts["flexibility"]
            is_flexible = fastener.properties.rigidity in [
                Rigidity.FLEXIBLE,
                Rigidity.SEMI_FLEXIBLE,
            ]

            if needs_flexibility and not is_flexible:
                return False

        # Check vibration resistance for dynamic loads
        if "load_type" in self.facts:
            load_type = self.facts["load_type"]
            if load_type in ["heavy_dynamic", "vibration"]:
                vib_idx = OrdinalScales.RESISTANCE.index(
                    fastener.properties.vibration_resistance.value
                )
                required_idx = OrdinalScales.RESISTANCE.index("good")

                if vib_idx < required_idx:
                    return False

        return True

    def evaluate_suggestion_conditions(self, suggestion_rule: SuggestionRule) -> bool:
        """Check if suggestion rule conditions are met by current facts"""
        for fact_key, expected_value in suggestion_rule.conditions.items():
            if fact_key not in self.facts:
                return False

            actual_value = self.facts[fact_key]

            # Handle list of acceptable values
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            elif actual_value != expected_value:
                return False

        return True

    def get_suggestions(self, fastener: Fastener) -> list[str]:
        """Generate context-specific suggestions from suggestion rules in kb.json"""
        suggestions = []

        for suggestion_rule in self.kb.suggestion_rules:
            # Check if this suggestion applies to this fastener
            applies = False

            if "all" in suggestion_rule.applies_to_fasteners:
                applies = True
            else:
                # Check if fastener name contains any of the applies_to patterns
                for pattern in suggestion_rule.applies_to_fasteners:
                    if pattern.lower() in fastener.name.lower():
                        applies = True
                        break

                # Also check category matches
                if fastener.category.value in suggestion_rule.applies_to_fasteners:
                    applies = True

            # If applies and conditions are met, add suggestion
            if applies and self.evaluate_suggestion_conditions(suggestion_rule):
                suggestions.append(suggestion_rule.suggestion)

        return suggestions

    def recommend_fasteners(self) -> list[tuple[Fastener, list[str]]]:
        """Get list of qualifying fasteners with suggestions (no scoring)"""
        self.infer()  # Run inference first

        qualifying_fasteners = []

        for fastener in self.kb.fasteners:
            if self.matches_fastener(fastener):
                suggestions = self.get_suggestions(fastener)
                qualifying_fasteners.append((fastener, suggestions))

        # Sort by priority from rules if applicable
        # For now, just return all qualifying fasteners
        return qualifying_fasteners
