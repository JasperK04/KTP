from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Callable

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
# Dataclasses
# -----------------------------------------------

@dataclass
class Question:
    """Represents a question to the user."""
    id: str
    text: str
    type: QuestionType
    choices: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type.value,
            "choices": self.choices,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        return cls(
            id=data["id"],
            text=data["text"],
            type=QuestionType(data["type"]),
            choices=data.get("choices", [])
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
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, any]) -> 'Rule':
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
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, any]) -> 'MaterialProperties':
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
            notes=data.get("notes", [])
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
            "special_conditions": self.special_conditions
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, any]) -> 'Fastener':
        return cls(
            name=data["name"],
            category=FastenerCategory(data["category"]),
            properties=MaterialProperties.from_dict(data["properties"]),
            requires_tools=data.get("requires_tools", []),
            surface_prep=data.get("surface_prep", []),
            curing_time=data.get("curing_time"),
            special_conditions=data.get("special_conditions", [])
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

    def load_from_file(self, filepath: str):
        """Load knowledge base from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.questions = [Question.from_dict(q) for q in data.get("questions", [])]
        self.fasteners = [Fastener.from_dict(f) for f in data.get("fasteners", [])]
        self.rules = [Rule.from_dict(r) for r in data.get("rules", [])]

    def save_to_file(self, filepath: str):
        """Save knowledge base to JSON file"""
        data = {
            "questions": [q.to_dict() for q in self.questions],
            "fasteners": [f.to_dict() for f in self.fasteners],
            "rules": [r.to_dict() for r in self.rules]
        }
        
        with open(filepath, 'w') as f:
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
    
    def reset(self):
        """Clear all facts and conclusions"""
        self.facts.clear()
        self.conclusions.clear()
    
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


# this is as far as i could get before running out of time. I dont want to submit code i didnt review. properly.
# check out the claude_inference_engine.py for the complete implementation