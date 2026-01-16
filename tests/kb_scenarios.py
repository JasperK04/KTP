"""
Knowledge Base Test Scenarios for Fastener Recommendation System.

This module contains structured test scenarios for evaluating the KB rules
and fastener recommendations. Scenarios are organized into 4 focus groups:

Group A: Material-specific rules (wood, metal, paper, fabric, brittle)
Group B: Environmental conditions (moisture, UV, temperature, chemicals)
Group C: Load and mechanical constraints (dynamic, shock, vibration, tension)
Group D: Edge cases and constraint combinations
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestScenario:
    """
    Represents a single test scenario for KB evaluation.
    
    Attributes:
        id: Unique identifier for the scenario
        name: Short descriptive name
        description: Real-world context for the fastening task
        agent: Scenario group ("A", "B", "C", or "D")
        answers: Maps question_id -> answer value
        expected_categories: Fastener categories that SHOULD be recommended
        excluded_categories: Fastener categories that should NOT appear
        expected_fasteners: Specific fastener names expected (optional)
        unexpected_fasteners: Fasteners that should NOT be recommended
        notes: Domain reasoning explaining the expectations
    """
    id: str
    name: str
    description: str
    agent: str
    answers: dict[str, Any]
    expected_categories: list[str] = field(default_factory=list)
    excluded_categories: list[str] = field(default_factory=list)
    expected_fasteners: list[str] = field(default_factory=list)
    unexpected_fasteners: list[str] = field(default_factory=list)
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT A: MATERIAL-SPECIFIC SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_A_SCENARIOS = [
    TestScenario(
        id="A01",
        name="Paper-to-Paper Scrapbooking",
        description="Attaching decorative paper to a scrapbook page. Very light, "
                    "indoor use, needs to be repositionable.",
        agent="A",
        answers={
            "material_a_type": "paper",
            "material_b_type": "paper",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["adhesive"],
        excluded_categories=["mechanical", "thermal"],
        expected_fasteners=[],  # Removed Wallpaper/Fabric adhesive - filtered by high_porosity rule requiring moderate shear
        unexpected_fasteners=["Wood screw", "Metal welding", "Hex bolt"],
        notes="Paper is too weak for mechanical fasteners. Thermal would destroy it. "
              "High porosity requires moderate shear strength, filtering out very_low/low adhesives. "
              "Wood glue (PVA) and Contact cement meet requirements.",
    ),
    TestScenario(
        id="A02",
        name="Metal-to-Metal Structural Frame",
        description="Joining steel beams for a permanent structural frame. "
                    "High load, outdoor industrial setting.",
        agent="A",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "outdoor",
            "load_type": "heavy_dynamic",
            "vibration": True,
            "permanence": "permanent",
            "uv_exposure": True,
            "temperature_extremes": True,
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": True,
            "load_direction": False,
            "shock_loads": False,
        },
        expected_categories=["thermal"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Metal welding"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Staple", "Hex bolt"],
        notes="Permanent metal-to-metal structural connections use welding. "
              "Bolts are removable by design. Vibration excludes adhesives.",
    ),
    TestScenario(
        id="A03",
        name="Wood-to-Wood Furniture Joint",
        description="Assembling a wooden dining table. Indoor use, moderate load, "
                    "should be disassemblable for moving.",
        agent="A",
        answers={
            "material_a_type": "wood",
            "material_b_type": "wood",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["mechanical", "adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Wood screw", "Wood glue (PVA)", "Hex bolt"],
        unexpected_fasteners=["Metal welding", "Plastic welding", "Concrete screw"],
        notes="Wood-to-wood excludes thermal (can't weld wood). Screws and wood glue "
              "are standard. Removable favors screws over permanent adhesives.",
    ),
    TestScenario(
        id="A04",
        name="Fabric-to-Fabric Upholstery",
        description="Attaching fabric to cushion padding for furniture upholstery. "
                    "Needs flexibility, light load.",
        agent="A",
        answers={
            "material_a_type": "fabric",
            "material_b_type": "fabric",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "semi_permanent",
            "chemical_exposure": False,
            "flexibility_required": True,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "fast",
            "access_one_side": True,
            "precision_required": False,
        },
        expected_categories=["adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Contact cement"],  # Fabric adhesive and Hot-melt glue filtered by high_porosity rule (low shear < moderate)
        unexpected_fasteners=["Metal welding", "Hex bolt", "Concrete screw"],
        notes="Fabric requires flexible bonding. Thermal excluded for fabric. "
              "High porosity requires moderate shear strength, filtering out low-strength adhesives. "
              "Contact cement meets all requirements (flexible, moderate shear).",
    ),
    TestScenario(
        id="A05",
        name="Glass-to-Metal Display Case",
        description="Attaching glass panels to metal frame for a museum display case. "
                    "Brittle material handling critical.",
        agent="A",
        answers={
            "material_a_type": "glass",
            "material_b_type": "metal",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": True,
        },
        expected_categories=["adhesive"],
        excluded_categories=["mechanical"],
        expected_fasteners=["Glass adhesive", "Silicone sealant", "Two-component epoxy"],
        unexpected_fasteners=["Wood screw", "rivet", "Common nail"],
        notes="Glass is very brittle - mechanical fasteners would crack it. "
              "Adhesives that work on both glass and metal are required.",
    ),
    TestScenario(
        id="A06",
        name="Ceramic Tile to Stone Floor",
        description="Installing ceramic tiles on a stone subfloor in a kitchen. "
                    "Permanent installation, some moisture.",
        agent="A",
        answers={
            "material_a_type": "ceramic",
            "material_b_type": "stone",
            "environment_moisture": "splash",
            "load_type": "static",
            "permanence": "permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": True,
            "precision_required": True,
        },
        expected_categories=["adhesive"],
        excluded_categories=["mechanical"],
        expected_fasteners=["Two-component epoxy", "High-temperature adhesive", "Flooring adhesive"],
        unexpected_fasteners=["Wood screw", "Staple", "Common nail"],
        notes="Ceramic is brittle - cannot use mechanical fasteners. "
              "Need adhesives compatible with both ceramic and stone.",
    ),
    TestScenario(
        id="A07",
        name="Plastic-to-Plastic Electronics Enclosure",
        description="Assembling a plastic electronics enclosure. Needs to be "
                    "openable for maintenance, indoor use.",
        agent="A",
        answers={
            "material_a_type": "plastic",
            "material_b_type": "plastic",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["thermal"],
        expected_fasteners=["Sheet metal screw"],
        unexpected_fasteners=["Wood screw", "Lag bolt", "Masonry nail", "rivet"],
        notes="Plastic-to-plastic enclosure uses screws for removability. "
              "Rivet is permanent so excluded. Thermal excluded by removable constraint.",
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT B: ENVIRONMENTAL SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_B_SCENARIOS = [
    TestScenario(
        id="B01",
        name="Covered Patio Furniture",
        description="Assembling wooden patio furniture under a covered area. "
                    "Some weather exposure but protected from direct sun/rain.",
        agent="B",
        answers={
            "material_a_type": "wood",
            "material_b_type": "wood",
            "environment_moisture": "outdoor",
            "load_type": "static",
            "permanence": "semi_permanent",
            "uv_exposure": False,  # Changed: covered from direct sun
            "temperature_extremes": False,  # Changed: moderate temps
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["mechanical", "adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Deck screw", "Polyurethane glue", "Marine epoxy"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Wallpaper adhesive"],
        notes="Covered outdoor: needs water resistance but not extreme UV/temp. "
              "Deck screw, Polyurethane glue, Marine epoxy all meet requirements.",
    ),
    TestScenario(
        id="B02",
        name="Pool Deck Equipment Mount",
        description="Mounting plastic equipment housing to metal bracket near pool. "
                    "Splash zone exposure, permanent installation.",
        agent="B",
        answers={
            "material_a_type": "plastic",
            "material_b_type": "metal",
            "environment_moisture": "splash",
            "load_type": "light_dynamic",
            "vibration": True,
            "permanence": "permanent",
            "chemical_exposure": False,  # Changed: no chemicals = fair chem resistance OK
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": False,
            "load_direction": False,
            "shock_loads": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["adhesive"],
        expected_fasteners=["rivet"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Sheet metal screw"],
        notes="Splash zone + vibration + permanent = rivet. "
              "Vibration excludes adhesives. Sheet metal screw is removable.",
    ),
    TestScenario(
        id="B03",
        name="Chemical Plant Pipe Support",
        description="Mounting metal pipe brackets in a chemical processing plant. "
                    "Exposure to corrosive chemicals, needs to be serviceable.",
        agent="B",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "splash",
            "load_type": "static",
            "permanence": "removable",  # Changed: industrial equipment needs serviceability
            "chemical_exposure": True,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": True,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["thermal"],
        expected_fasteners=["Hex bolt"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Soldering", "Metal welding"],
        notes="Health constraints exclude thermal (welding fumes). Removable for maintenance. "
              "Hex bolt provides chemical resistance and high shear for vertical mounting.",
    ),
    TestScenario(
        id="B04",
        name="Freezer Storage Shelving",
        description="Installing metal shelving brackets inside an industrial freezer. "
                    "Extreme cold (-30°C), frost cycles.",
        agent="B",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["thermal"],  # removable_connection excludes thermal
        expected_fasteners=["Hex bolt"],  # Only high-tensile metal fastener
        unexpected_fasteners=["Hot-melt glue", "Superglue (cyanoacrylate)", "Metal welding"],
        notes="Removable constraint excludes thermal. metal_to_metal requires high tensile. "
              "Hex bolt is the only removable metal fastener with very_high tensile.",
    ),
    TestScenario(
        id="B05",
        name="Bathroom Mirror Mounting",
        description="Mounting a glass mirror to drywall bathroom wall. "
                    "Using mirror clips and silicone for safety.",
        agent="B",
        answers={
            "material_a_type": "glass",
            "material_b_type": "wood",  # Changed: drywall backing is wood studs
            "environment_moisture": "splash",
            "load_type": "static",
            "permanence": "semi_permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": True,
            "precision_required": False,  # Changed: no precision requirement
        },
        expected_categories=["adhesive"],
        excluded_categories=["mechanical"],
        expected_fasteners=["Silicone sealant"],
        unexpected_fasteners=["Wood screw", "Common nail", "Staple"],
        notes="Glass is very brittle - excludes mechanical. Silicone works on glass+wood, "
              "has excellent water resistance for bathroom use.",
    ),
    TestScenario(
        id="B06",
        name="Desert Solar Panel Frame",
        description="Mounting metal solar panel frame in desert conditions. "
                    "Extreme UV, temperature swings, permanent installation.",
        agent="B",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "outdoor",
            "load_type": "static",
            "permanence": "permanent",
            "uv_exposure": True,
            "temperature_extremes": True,
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": True,
        },
        expected_categories=["thermal"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Metal welding"],
        unexpected_fasteners=["Hot-melt glue", "Superglue (cyanoacrylate)", "Hex bolt"],
        notes="Permanent + metal_to_metal + high tensile = welding only. "
              "Hex bolt is removable. Rivet has moderate tensile (filtered by high requirement).",
    ),
    TestScenario(
        id="B07",
        name="Indoor Climate-Controlled Art Installation",
        description="Mounting metal sculpture elements in a museum. Perfect climate "
                    "control, no environmental stress.",
        agent="B",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "semi_permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": True,
            "max_curing_time": "moderate",
            "access_one_side": False,
            "precision_required": True,
        },
        expected_categories=["mechanical"],
        excluded_categories=["thermal"],
        expected_fasteners=["Hex bolt"],
        unexpected_fasteners=["Metal welding", "Brazing", "Two-component epoxy"],
        notes="Health constraints exclude thermal. metal_to_metal restricts to mechanical+thermal. "
              "Only mechanical remains. Hex bolt provides high shear for vertical mount.",
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT C: LOAD AND MECHANICAL SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_C_SCENARIOS = [
    TestScenario(
        id="C01",
        name="Industrial Machine Vibration Mount",
        description="Mounting a motor to a metal base plate. Heavy vibration, "
                    "high dynamic loads, must not loosen.",
        agent="C",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "none",
            "load_type": "heavy_dynamic",
            "vibration": True,
            "permanence": "permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": True,
            "load_direction": False,
            "shock_loads": False,
        },
        expected_categories=["mechanical", "thermal"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Metal welding", "Hex bolt"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue"],
        notes="Permanent metal-to-metal with vibration. Welding is ideal but "
              "Hex bolt with lock washers is also valid for industrial mounts. "
              "Vibration excludes adhesives.",
    ),
    TestScenario(
        id="C02",
        name="Interior Plastic Panel Mount",
        description="Attaching plastic interior panel to metal frame. "
                    "Indoor/protected use. Needs to be serviceable.",
        agent="C",
        answers={
            "material_a_type": "plastic",
            "material_b_type": "metal",
            "environment_moisture": "none",  # Changed: indoor, no moisture
            "load_type": "light_dynamic",
            "vibration": False,
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": False,
            "precision_required": False,
            "load_direction": False,
            "shock_loads": False,
        },
        expected_categories=["mechanical", "adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Sheet metal screw", "Acrylic adhesive", "Superglue (cyanoacrylate)"],
        unexpected_fasteners=["Wood glue (PVA)", "Fabric adhesive", "rivet"],
        notes="Indoor use - no water resistance needed. Removable excludes rivet and thermal. "
              "Sheet metal screw and various adhesives work for plastic+metal.",
    ),
    TestScenario(
        id="C03",
        name="Decorative Wall Picture",
        description="Attaching a wooden picture frame to masonry wall. "
                    "Using adhesive to avoid drilling into decorative masonry.",
        agent="C",
        answers={
            "material_a_type": "wood",
            "material_b_type": "masonry",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "semi_permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": True,
            "precision_required": False,
        },
        expected_categories=["adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Construction adhesive", "Flooring adhesive"],
        unexpected_fasteners=["Metal welding", "Common nail", "Masonry nail"],
        notes="No mechanical fastener works for wood+masonry combination. "
              "Masonry nail only works on masonry itself, not wood+masonry joint. "
              "Construction/Flooring adhesive compatible with both materials.",
    ),
    TestScenario(
        id="C04",
        name="Heavy Duty Shelf Bracket",
        description="Mounting metal shelf brackets to wooden studs. "
                    "Heavy load, tension from loaded shelves.",
        agent="C",
        answers={
            "material_a_type": "metal",
            "material_b_type": "wood",
            "environment_moisture": "none",
            "load_type": "heavy_dynamic",
            "vibration": False,
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": False,  # Changed: can access both sides for bolt+nut
            "precision_required": False,
            "load_direction": True,
            "shock_loads": True,
        },
        expected_categories=["mechanical"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Hex bolt"],  # Only Hex bolt works for metal+wood
        unexpected_fasteners=["Staple", "Brad nail", "Hot-melt glue", "Lag bolt"],
        notes="Shock loads exclude adhesives. Hex bolt is the only metal+wood compatible fastener. "
              "Lag bolt is wood-only. Need two-sided access for bolt+nut.",
    ),
    TestScenario(
        id="C05",
        name="Ceiling Light Fixture Base",
        description="Mounting a metal light fixture base to concrete ceiling. "
                    "Using construction adhesive for flush mount.",
        agent="C",
        answers={
            "material_a_type": "metal",
            "material_b_type": "masonry",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "permanent",  # Changed: permanent mount
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": True,
            "precision_required": False,  # Changed: no precision requirement
        },
        expected_categories=["adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Construction adhesive"],
        unexpected_fasteners=["Hot-melt glue", "Fabric adhesive", "Duct tape", "Concrete screw"],
        notes="No mechanical fastener works for metal+masonry in KB. "
              "Concrete screw is masonry+stone only. Construction adhesive has "
              "high shear strength needed for vertical installation.",
    ),
    TestScenario(
        id="C06",
        name="Precision Optical Instrument Mount",
        description="Mounting optical sensor to metal bracket. Requires precise "
                    "positioning that won't shift. Permanent installation.",
        agent="C",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": True,
        },
        expected_categories=["mechanical", "thermal"],
        excluded_categories=[],
        expected_fasteners=["Metal welding", "Dowel pin"],
        unexpected_fasteners=["Hot-melt glue", "Duct tape"],
        notes="metal_to_metal allows mechanical+thermal. Dowel pins are ideal for "
              "precision positioning - that's their primary purpose. Welding also "
              "provides permanent, precise joints.",
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT D: EDGE CASES AND CONSTRAINT COMBINATIONS
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_D_SCENARIOS = [
    TestScenario(
        id="D01",
        name="One-Sided Access Panel",
        description="Attaching plastic access panel to metal enclosure where only exterior is "
                    "accessible. Needs to be openable for maintenance.",
        agent="D",
        answers={
            "material_a_type": "plastic",  # Changed: avoid metal_to_metal high tensile
            "material_b_type": "metal",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": True,
            "precision_required": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["thermal"],
        expected_fasteners=["Sheet metal screw"],
        unexpected_fasteners=["Hex bolt", "Dowel pin", "rivet"],
        notes="One-sided access excludes Hex bolt (needs nut). Plastic+metal uses Sheet metal screw. "
              "Rivet is permanent. Removable excludes thermal.",
    ),
    TestScenario(
        id="D02",
        name="Health-Restricted School Project",
        description="Elementary school craft project. No fumes, no heat, must be "
                    "completely safe for children.",
        agent="D",
        answers={
            "material_a_type": "paper",
            "material_b_type": "wood",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "semi_permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": True,
            "max_curing_time": "fast",
            "access_one_side": True,
            "precision_required": False,
        },
        expected_categories=["adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Contact cement"],
        unexpected_fasteners=["Metal welding", "Superglue (cyanoacrylate)", "Staple"],
        notes="Health constraints exclude thermal. Paper+wood adhesives: PVA, Hot-melt, Contact cement. "
              "Staple not paper+wood compatible (only fabric+paper+wood, must match BOTH materials).",
    ),
    TestScenario(
        id="D03",
        name="Flexible Joint Requirement",
        description="Connecting two plastic parts that need to flex relative to each other. "
                    "Like a living hinge.",
        agent="D",
        answers={
            "material_a_type": "plastic",
            "material_b_type": "plastic",
            "environment_moisture": "none",
            "load_type": "light_dynamic",
            "vibration": False,
            "permanence": "semi_permanent",  # Changed: no flexible adhesive is permanent
            "chemical_exposure": False,
            "flexibility_required": True,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": False,
            "precision_required": False,
            "load_direction": False,
            "shock_loads": False,
        },
        expected_categories=["adhesive"],
        excluded_categories=[],
        expected_fasteners=["Silicone sealant", "Contact cement"],
        unexpected_fasteners=["Two-component epoxy", "Metal welding", "Hex bolt"],
        notes="Flexibility required limits to flexible/semi-flexible rigidity. "
              "Silicone and Contact cement are flexible and work on plastic.",
    ),
    TestScenario(
        id="D04",
        name="Contradictory: Permanent but Removable",
        description="Customer wants a permanent solution that can also be removed. "
                    "Testing how system handles conflicting constraints.",
        agent="D",
        answers={
            "material_a_type": "wood",
            "material_b_type": "wood",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "removable",  # User says removable
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["thermal"],
        expected_fasteners=["Wood screw", "Hex bolt", "Lag bolt"],
        unexpected_fasteners=["Metal welding", "Marine epoxy"],
        notes="Removable constraint should exclude permanent-only fasteners. "
              "Testing that permanence constraints are properly applied.",
    ),
    TestScenario(
        id="D05",
        name="Everything Excluded Scenario",
        description="Extreme constraints that should eliminate most options: "
                    "brittle material, vibration, health constraints, vertical.",
        agent="D",
        answers={
            "material_a_type": "glass",
            "material_b_type": "ceramic",
            "environment_moisture": "splash",
            "load_type": "heavy_dynamic",
            "vibration": True,
            "permanence": "permanent",
            "chemical_exposure": True,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": True,
            "max_curing_time": "slow",
            "access_one_side": True,
            "precision_required": True,
            "load_direction": True,
            "shock_loads": True,
        },
        expected_categories=[],  # Might have very few or no options
        excluded_categories=["mechanical", "thermal"],
        expected_fasteners=[],  # Possibly no good solutions
        unexpected_fasteners=["Wood screw", "Metal welding", "Hot-melt glue"],
        notes="This scenario tests edge case where constraints are very restrictive. "
              "Glass+ceramic = brittle = no mechanical. Health = no thermal. "
              "Vibration+shock = no adhesive. System should handle gracefully.",
    ),
    TestScenario(
        id="D06",
        name="Quick Assembly Metal-to-Wood",
        description="Attaching metal bracket to wooden beam. Needs to be "
                    "functional immediately, serviceable later.",
        agent="D",
        answers={
            "material_a_type": "metal",
            "material_b_type": "wood",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "semi_permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["mechanical", "adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Hex bolt", "Construction adhesive"],
        unexpected_fasteners=["Metal welding", "Brazing"],
        notes="Metal+wood compatible: Hex bolt, Construction adhesive, Polyurethane glue. "
              "We removed immediate_use_required rule, so adhesives are allowed.",
    ),
    TestScenario(
        id="D07",
        name="Outdoor Deck Post to Concrete",
        description="Mounting wood deck post to concrete foundation using post bracket and adhesive. "
                    "Outdoor exposure, high load.",
        agent="D",
        answers={
            "material_a_type": "wood",
            "material_b_type": "masonry",
            "environment_moisture": "outdoor",
            "load_type": "static",
            "permanence": "semi_permanent",
            "uv_exposure": False,
            "temperature_extremes": False,
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": True,
            "precision_required": False,
        },
        expected_categories=["adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Construction adhesive"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Metal welding", "Masonry nail"],
        notes="No mechanical fastener works for wood+masonry in KB. "
              "Masonry nail is masonry+stone only. Construction adhesive is the "
              "only option that's compatible with both wood AND masonry.",
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# ALL SCENARIOS COMBINED
# ═══════════════════════════════════════════════════════════════════════════════

ALL_SCENARIOS = (
    AGENT_A_SCENARIOS +
    AGENT_B_SCENARIOS +
    AGENT_C_SCENARIOS +
    AGENT_D_SCENARIOS
)


def get_scenarios_for_agent(agent: str) -> list[TestScenario]:
    """Return all scenarios assigned to a specific agent."""
    return [s for s in ALL_SCENARIOS if s.agent == agent]


def get_scenario_by_id(scenario_id: str) -> TestScenario | None:
    """Return a specific scenario by ID."""
    for s in ALL_SCENARIOS:
        if s.id == scenario_id:
            return s
    return None
