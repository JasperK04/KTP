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


@dataclass
class UsageConstraints:
    """
    Represents user-imposed constraints and preferences.
    """

    permanence: Permanence
    flexibility_required: bool
    orientation_vertical: bool
    health_constraints: bool
    one_side_accessible: bool
    max_curing_time: Optional[str]


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
    allowed_categories: set[str] = field(default_factory=set)
    excluded_categories: set[str] = field(default_factory=set)


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
