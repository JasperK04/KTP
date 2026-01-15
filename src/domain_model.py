"""
Domain Model for the Fastener Recommendation Knowledge System.

This module defines the domain objects used in the Knowledge Technology
Practical (KTP) project. The domain model specifies *what* entities exist
in the problem domain, which attributes they have, and how they relate.

The domain model contains no inference logic, no rules, and no user
interaction code. It is purely declarative and serves as the foundation
on which the rule model and inference mechanisms operate.

The central domain object is a FasteningTask, which represents one concrete
fastening problem instance. During inference, rules add and refine knowledge
by updating attributes of this object and its sub-components.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MaterialType(Enum):
    """
    Enumeration of material types that can be joined.
    """

    WOOD = "wood"
    METAL = "metal"
    PAPER = "paper"
    PLASTIC = "plastic"
    GLASS = "glass"
    CERAMIC = "ceramic"
    STONE = "stone"
    MASONRY = "masonry"
    FABRIC = "fabric"


class MoistureExposure(Enum):
    """
    Enumeration of moisture exposure conditions.
    """

    NONE = "none"
    SPLASH = "splash"
    OUTDOOR = "outdoor"
    SUBMERGED = "submerged"


class LoadType(Enum):
    """
    Enumeration of mechanical load types.
    """

    STATIC = "static"
    LIGHT_DYNAMIC = "light_dynamic"
    HEAVY_DYNAMIC = "heavy_dynamic"


class Permanence(Enum):
    """
    Enumeration describing whether a joint must be removable or permanent.
    """

    REMOVABLE = "removable"
    SEMI_PERMANENT = "semi_permanent"
    PERMANENT = "permanent"


class Rigidity(Enum):
    """
    Enumeration describing the rigidity of a fastener after installation.
    """

    FLEXIBLE = "flexible"
    SEMI_FLEXIBLE = "semi_flexible"
    RIGID = "rigid"


class StrengthLevel(Enum):
    """
    Ordinal enumeration describing mechanical strength levels.
    """

    NONE = "none"
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ResistanceLevel(Enum):
    """
    Ordinal enumeration describing resistance levels.
    """

    NONE = "none"
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


# ─────────────────────────────────────────────
# MATERIAL OBJECTS
# ─────────────────────────────────────────────
@dataclass
class Material:
    """
    Represents a single material surface involved in a fastening task.

    This object captures intrinsic material properties that influence
    fastening decisions, such as brittleness and base strength.
    """

    material_type: MaterialType
    porosity: str
    brittleness: str
    base_strength: StrengthLevel

    def to_dict(self) -> dict:
        """
        Convert the Material object to a dictionary representation.

        :return: A dictionary containing the material's attributes.
        """
        return {
            "material_type": self.material_type.value if self.material_type else None,
            "porosity": self.porosity,
            "brittleness": self.brittleness,
            "base_strength": self.base_strength.value if self.base_strength else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Material":
        """
        Create a Material object from a dictionary representation.

        :param data: A dictionary containing the material's attributes.
        :return: A Material object.
        """
        return cls(
            material_type=MaterialType(data["material_type"])
            if data["material_type"] is not None
            else None,  # pyright: ignore[reportArgumentType]
            porosity=data["porosity"],
            brittleness=data["brittleness"],
            base_strength=StrengthLevel(data["base_strength"])
            if data["base_strength"] is not None
            else None,  # pyright: ignore[reportArgumentType]
        )


@dataclass
class MaterialPair:
    """
    Represents a pair of materials being joined.

    Rules typically reason over the relationship between two materials,
    rather than over individual materials in isolation.
    """

    material_a: Material
    material_b: Material

    def same_material(self) -> bool:
        """
        Check whether both materials are of the same type.

        :return: True if both materials have the same material type.
        """
        return self.material_a.material_type == self.material_b.material_type

    def to_dict(self) -> dict:
        """
        Convert the MaterialPair object to a dictionary representation.

        :return: A dictionary containing the attributes of both materials.
        """
        return {
            "material_a": self.material_a.to_dict(),
            "material_b": self.material_b.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MaterialPair":
        """
        Create a MaterialPair object from a dictionary representation.

        :param data: A dictionary containing the attributes of both materials.
        :return: A MaterialPair object.
        """
        return cls(
            material_a=Material.from_dict(data["material_a"]),
            material_b=Material.from_dict(data["material_b"]),
        )


# ─────────────────────────────────────────────
# CONTEXT OBJECTS
# ─────────────────────────────────────────────
@dataclass
class Environment:
    """
    Represents environmental conditions affecting the fastening task.
    """

    moisture: MoistureExposure
    chemical_exposure: bool
    uv_exposure: bool
    temperature_extremes: bool

    def to_dict(self) -> dict:
        """
        Convert the Environment object to a dictionary representation.

        :return: A dictionary containing the environment's attributes.
        """
        return {
            "moisture": self.moisture.value,
            "chemical_exposure": self.chemical_exposure,
            "uv_exposure": self.uv_exposure,
            "temperature_extremes": self.temperature_extremes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Environment":
        """
        Create an Environment object from a dictionary representation.

        :param data: A dictionary containing the environment's attributes.
        :return: An Environment object.
        """
        return cls(
            moisture=MoistureExposure(data["moisture"]),
            chemical_exposure=data["chemical_exposure"],
            uv_exposure=data["uv_exposure"],
            temperature_extremes=data["temperature_extremes"],
        )


@dataclass
class LoadCondition:
    """
    Represents mechanical loading conditions applied to the joint.

    The required strength may initially be unknown and is typically
    derived by rules during inference.
    """

    load_type: LoadType
    vibration: bool
    tension_dominant: bool
    shock_loads: bool
    required_strength: Optional[StrengthLevel] = None

    def to_dict(self) -> dict:
        """
        Convert the LoadCondition object to a dictionary representation.

        :return: A dictionary containing the load condition's attributes.
        """
        return {
            "load_type": self.load_type.value,
            "vibration": self.vibration,
            "tension_dominant": self.tension_dominant,
            "shock_loads": self.shock_loads,
            "required_strength": self.required_strength.value
            if self.required_strength
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LoadCondition":
        """
        Create a LoadCondition object from a dictionary representation.

        :param data: A dictionary containing the load condition's attributes.
        :return: A LoadCondition object.
        """
        return cls(
            load_type=LoadType(data["load_type"]),
            vibration=data["vibration"],
            tension_dominant=data["tension_dominant"],
            shock_loads=data["shock_loads"],
            required_strength=StrengthLevel(data["required_strength"])
            if data["required_strength"]
            else None,
        )


@dataclass
class UsageConstraints:
    """
    Represents user-imposed constraints and preferences.
    """

    permanence: Permanence
    flexibility_required: bool
    orientation_vertical: bool
    precision_required: bool
    health_constraints: bool
    one_side_accessable: bool
    max_curing_time: Optional[str]

    def to_dict(self) -> dict:
        """
        Convert the UsageConstraints object to a dictionary representation.

        :return: A dictionary containing the usage constraints' attributes.
        """
        return {
            "permanence": self.permanence.value,
            "flexibility_required": self.flexibility_required,
            "orientation_vertical": self.orientation_vertical,
            "precision_required": self.precision_required,
            "health_constraints": self.health_constraints,
            "one_side_accessable": self.one_side_accessable,
            "max_curing_time": self.max_curing_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UsageConstraints":
        """
        Create a UsageConstraints object from a dictionary representation.

        :param data: A dictionary containing the usage constraints' attributes.
        :return: A UsageConstraints object.
        """
        return cls(
            permanence=Permanence(data["permanence"]),
            flexibility_required=data["flexibility_required"],
            orientation_vertical=data["orientation_vertical"],
            precision_required=data["precision_required"],
            health_constraints=data["health_constraints"],
            one_side_accessable=data["one_side_accessable"],
            max_curing_time=data["max_curing_time"],
        )


# ─────────────────────────────────────────────
# DERIVED KNOWLEDGE
# ─────────────────────────────────────────────
@dataclass
class DerivedRequirements:
    """
    Stores requirements inferred during reasoning.

    This object represents intermediate and derived knowledge, such as
    minimum strength or excluded fastener categories. It is the primary
    target of rule actions.
    """

    min_tensile_strength: StrengthLevel = StrengthLevel.NONE
    min_shear_strength: StrengthLevel = StrengthLevel.NONE

    min_water_resistance: ResistanceLevel = ResistanceLevel.NONE
    min_temperature_resistance: ResistanceLevel = ResistanceLevel.NONE
    min_uv_resistance: ResistanceLevel = ResistanceLevel.NONE
    min_vibration_resistance: ResistanceLevel = ResistanceLevel.NONE
    min_chemical_resistance: ResistanceLevel = ResistanceLevel.NONE

    allowed_rigidities: set[Rigidity] = field(default_factory=set)
    allowed_permanence: set[Permanence] = field(default_factory=set)
    allowed_categories: set[str] = field(default_factory=set)
    excluded_categories: set[str] = field(default_factory=set)

    def to_dict(self) -> dict:
        """
        Convert the DerivedRequirements object to a dictionary representation.

        :return: A dictionary containing the derived requirements' attributes.
        """
        return {
            "min_tensile_strength": self.min_tensile_strength.value,
            "min_shear_strength": self.min_shear_strength.value,
            "min_water_resistance": self.min_water_resistance.value,
            "min_temperature_resistance": self.min_temperature_resistance.value,
            "min_uv_resistance": self.min_uv_resistance.value,
            "min_vibration_resistance": self.min_vibration_resistance.value,
            "min_chemical_resistance": self.min_chemical_resistance.value,
            "allowed_rigidities": [r.value for r in self.allowed_rigidities],
            "allowed_permanence": [p.value for p in self.allowed_permanence],
            "allowed_categories": list(self.allowed_categories),
            "excluded_categories": list(self.excluded_categories),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DerivedRequirements":
        """
        Create a DerivedRequirements object from a dictionary representation.

        :param data: A dictionary containing the derived requirements' attributes.
        :return: A DerivedRequirements object.
        """
        return cls(
            min_tensile_strength=StrengthLevel(data["min_tensile_strength"]),
            min_shear_strength=StrengthLevel(data["min_shear_strength"]),
            min_water_resistance=ResistanceLevel(data["min_water_resistance"]),
            min_temperature_resistance=ResistanceLevel(
                data["min_temperature_resistance"]
            ),
            min_uv_resistance=ResistanceLevel(data["min_uv_resistance"]),
            min_vibration_resistance=ResistanceLevel(data["min_vibration_resistance"]),
            min_chemical_resistance=ResistanceLevel(data["min_chemical_resistance"]),
            allowed_rigidities={Rigidity(r) for r in data["allowed_rigidities"]},
            allowed_permanence={Permanence(p) for p in data["allowed_permanence"]},
            allowed_categories=set(data["allowed_categories"]),
            excluded_categories=set(data["excluded_categories"]),
        )


# ─────────────────────────────────────────────
# CENTRAL DOMAIN OBJECT
# ─────────────────────────────────────────────
@dataclass
class FasteningTask:
    """
    Represents one concrete fastening problem.

    The FasteningTask aggregates all relevant domain objects and acts as
    the central state modified by inference. Rules do not select fasteners
    directly; instead, they update the requirements stored in this object.
    """

    materials: MaterialPair
    environment: Environment
    load: LoadCondition
    constraints: UsageConstraints
    requirements: DerivedRequirements = field(default_factory=DerivedRequirements)

    def to_dict(self) -> dict:
        """
        Convert the FasteningTask object to a dictionary representation.

        :return: A dictionary containing the fastening task's attributes.
        """
        return {
            "materials": self.materials.to_dict(),
            "environment": self.environment.to_dict(),
            "load": self.load.to_dict(),
            "constraints": self.constraints.to_dict(),
            "requirements": self.requirements.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FasteningTask":
        """
        Create a FasteningTask object from a dictionary representation.

        :param data: A dictionary containing the fastening task's attributes.
        :return: A FasteningTask object.
        """
        return cls(
            materials=MaterialPair.from_dict(data["materials"]),
            environment=Environment.from_dict(data["environment"]),
            load=LoadCondition.from_dict(data["load"]),
            constraints=UsageConstraints.from_dict(data["constraints"]),
            requirements=DerivedRequirements.from_dict(data["requirements"]),
        )


# ─────────────────────────────────────────────
# FASTENER OBJECT (CANDIDATE)
# ─────────────────────────────────────────────
@dataclass
class Fastener:
    """
    Represents a candidate fastening method.
    """

    name: str
    category: str
    compatible_materials: list[MaterialType]

    tensile_strength: StrengthLevel
    shear_strength: StrengthLevel

    water_resistance: ResistanceLevel
    temperature_resistance: ResistanceLevel
    uv_resistance: ResistanceLevel
    vibration_resistance: ResistanceLevel
    chemical_resistance: ResistanceLevel

    rigidity: Rigidity
    permanence: Permanence

    requires_two_sided_access: bool

    def to_dict(self) -> dict:
        """
        Convert the Fastener object to a dictionary representation.

        :return: A dictionary containing the fastener's attributes.
        """
        return {
            "name": self.name,
            "category": self.category,
            "compatible_materials": [m.value for m in self.compatible_materials],
            "tensile_strength": self.tensile_strength.value,
            "shear_strength": self.shear_strength.value,
            "water_resistance": self.water_resistance.value,
            "temperature_resistance": self.temperature_resistance.value,
            "uv_resistance": self.uv_resistance.value,
            "vibration_resistance": self.vibration_resistance.value,
            "chemical_resistance": self.chemical_resistance.value,
            "rigidity": self.rigidity.value,
            "permanence": self.permanence.value,
            "requires_two_sided_access": self.requires_two_sided_access,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Fastener":
        """
        Create a Fastener object from a dictionary representation.

        :param data: A dictionary containing the fastener's attributes.
        :return: A Fastener object.
        """
        return cls(
            name=data["name"],
            category=data["category"],
            compatible_materials=[
                MaterialType(m) for m in data["compatible_materials"]
            ],
            tensile_strength=StrengthLevel(data["tensile_strength"]),
            shear_strength=StrengthLevel(data["shear_strength"]),
            water_resistance=ResistanceLevel(data["water_resistance"]),
            temperature_resistance=ResistanceLevel(data["temperature_resistance"]),
            uv_resistance=ResistanceLevel(data["uv_resistance"]),
            vibration_resistance=ResistanceLevel(data["vibration_resistance"]),
            chemical_resistance=ResistanceLevel(data["chemical_resistance"]),
            rigidity=Rigidity(data["rigidity"]),
            permanence=Permanence(data["permanence"]),
            requires_two_sided_access=data["requires_two_sided_access"],
        )
