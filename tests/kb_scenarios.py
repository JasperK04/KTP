"""
Knowledge Base Test Scenarios for Fastener Recommendation System.

This module contains structured test scenarios for evaluating the KB rules
and fastener recommendations. Each scenario is assigned to one of 4 LLM agents
for review and analysis.

Agent Assignments:
- Agent A: Material-specific rules (wood, metal, paper, fabric, brittle)
- Agent B: Environmental conditions (moisture, UV, temperature, chemicals)
- Agent C: Load and mechanical constraints (dynamic, shock, vibration, tension)
- Agent D: Edge cases and constraint combinations
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
        agent: Assigned agent ("A", "B", "C", or "D")
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
        expected_fasteners=["Wallpaper adhesive", "Fabric adhesive"],
        unexpected_fasteners=["Wood screw", "Metal welding", "Hex bolt"],
        notes="Paper is too weak for mechanical fasteners. Thermal would destroy it. "
              "Only light adhesives are appropriate.",
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
            "tension_dominant": False,
            "shock_loads": False,
        },
        expected_categories=["mechanical", "thermal"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Metal welding", "Hex bolt", "rivet"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Staple"],
        notes="Metal-to-metal with high loads favors welding or heavy mechanical. "
              "Vibration excludes adhesives. Thermal methods excel here.",
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
        expected_fasteners=["Fabric adhesive", "Contact cement", "Hot-melt glue"],
        unexpected_fasteners=["Metal welding", "Hex bolt", "Concrete screw"],
        notes="Fabric requires flexible bonding. Thermal excluded for fabric. "
              "Mechanical generally unsuitable except staples for wood backing.",
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
            "precision_required": True,
        },
        expected_categories=["mechanical"],
        excluded_categories=[],
        expected_fasteners=["Sheet metal screw", "rivet"],
        unexpected_fasteners=["Wood screw", "Lag bolt", "Masonry nail"],
        notes="Plastic-to-plastic can use screws or welding. Removable constraint "
              "favors screws. Immediate use excludes slow-curing adhesives.",
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT B: ENVIRONMENTAL SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_B_SCENARIOS = [
    TestScenario(
        id="B01",
        name="Outdoor Garden Furniture",
        description="Assembling wooden garden furniture exposed to rain and sun. "
                    "Must withstand weather year-round.",
        agent="B",
        answers={
            "material_a_type": "wood",
            "material_b_type": "wood",
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
            "precision_required": False,
        },
        expected_categories=["mechanical", "adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Deck screw", "Polyurethane glue", "Marine epoxy"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Wallpaper adhesive"],
        notes="Outdoor exposure requires excellent UV and water resistance. "
              "Standard wood glue has poor water resistance. Deck screws are designed for this.",
    ),
    TestScenario(
        id="B02",
        name="Submerged Pool Equipment",
        description="Mounting plastic fittings to metal pool pump housing. "
                    "Constantly underwater, chlorine exposure.",
        agent="B",
        answers={
            "material_a_type": "plastic",
            "material_b_type": "metal",
            "environment_moisture": "submerged",
            "load_type": "light_dynamic",
            "vibration": True,
            "permanence": "permanent",
            "uv_exposure": False,
            "temperature_extremes": False,
            "chemical_exposure": True,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": False,
            "tension_dominant": False,
            "shock_loads": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Sheet metal screw", "rivet"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Fabric adhesive"],
        notes="Submerged + vibration + chemicals creates harsh conditions. "
              "Most adhesives fail. Need excellent water and chemical resistance.",
    ),
    TestScenario(
        id="B03",
        name="Chemical Plant Pipe Support",
        description="Mounting metal pipe brackets in a chemical processing plant. "
                    "Exposure to corrosive chemicals, high temperatures.",
        agent="B",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "splash",
            "load_type": "static",
            "permanence": "permanent",
            "chemical_exposure": True,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": True,
            "max_curing_time": "slow",
            "access_one_side": False,
            "precision_required": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["thermal", "adhesive"],
        expected_fasteners=["Hex bolt", "rivet"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Soldering"],
        notes="Health constraints exclude thermal (welding fumes). Chemical exposure "
              "requires good chemical resistance. Vertical orientation needs shear strength.",
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
        expected_categories=["mechanical", "thermal"],
        excluded_categories=[],
        expected_fasteners=["Hex bolt", "Sheet metal screw", "Metal welding"],
        unexpected_fasteners=["Hot-melt glue", "Superglue (cyanoacrylate)"],
        notes="Extreme cold degrades many adhesives. Mechanical and thermal methods "
              "maintain strength at low temperatures. Immediate use favors mechanical.",
    ),
    TestScenario(
        id="B05",
        name="Bathroom Mirror Mounting",
        description="Mounting a glass mirror to masonry bathroom wall. "
                    "High humidity, occasional splashing.",
        agent="B",
        answers={
            "material_a_type": "glass",
            "material_b_type": "masonry",
            "environment_moisture": "splash",
            "load_type": "static",
            "permanence": "permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": True,
            "precision_required": True,
        },
        expected_categories=["adhesive"],
        excluded_categories=["mechanical"],
        expected_fasteners=["Glass adhesive", "Silicone sealant"],
        unexpected_fasteners=["Wood screw", "Common nail", "Staple"],
        notes="Glass is brittle - no mechanical fasteners. Need water-resistant "
              "adhesive that works on both glass and masonry. Silicone excels here.",
    ),
    TestScenario(
        id="B06",
        name="Desert Solar Panel Frame",
        description="Mounting metal solar panel frame in desert conditions. "
                    "Extreme UV, temperature swings, no moisture.",
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
        expected_categories=["mechanical", "thermal"],
        excluded_categories=[],
        expected_fasteners=["Hex bolt", "Metal welding", "rivet"],
        unexpected_fasteners=["Hot-melt glue", "Superglue (cyanoacrylate)"],
        notes="Extreme UV and temperature swings degrade most adhesives. "
              "Metal fasteners and welding provide long-term durability.",
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
        expected_categories=["mechanical", "adhesive"],
        excluded_categories=["thermal"],
        expected_fasteners=["Hex bolt", "Two-component epoxy", "Metal epoxy"],
        unexpected_fasteners=["Metal welding", "Brazing"],
        notes="Health constraints (museum air quality) exclude thermal methods. "
              "Protected environment allows more adhesive options.",
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
            "tension_dominant": False,
            "shock_loads": False,
        },
        expected_categories=["mechanical", "thermal"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Hex bolt", "Metal welding", "rivet"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Superglue (cyanoacrylate)"],
        notes="Heavy vibration excludes adhesives. Need high vibration resistance. "
              "Bolts with lock washers or welding are standard for machinery.",
    ),
    TestScenario(
        id="C02",
        name="Automotive Impact Bumper",
        description="Attaching plastic bumper cover to metal frame. Must absorb "
                    "shock impacts without detaching.",
        agent="C",
        answers={
            "material_a_type": "plastic",
            "material_b_type": "metal",
            "environment_moisture": "outdoor",
            "load_type": "heavy_dynamic",
            "vibration": True,
            "permanence": "semi_permanent",
            "uv_exposure": True,
            "temperature_extremes": True,
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": True,
            "precision_required": False,
            "tension_dominant": False,
            "shock_loads": True,
        },
        expected_categories=["mechanical"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Sheet metal screw", "rivet"],
        unexpected_fasteners=["Wood glue (PVA)", "Fabric adhesive", "Wallpaper adhesive"],
        notes="Shock loads exclude most adhesives. Need good shear strength for impacts. "
              "Vibration further restricts to mechanical fasteners.",
    ),
    TestScenario(
        id="C03",
        name="Decorative Wall Picture",
        description="Hanging a lightweight picture frame on drywall. Minimal load, "
                    "static, needs to be repositionable.",
        agent="C",
        answers={
            "material_a_type": "wood",
            "material_b_type": "masonry",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": True,
            "precision_required": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["thermal", "adhesive"],
        expected_fasteners=["Common nail", "Masonry nail"],
        unexpected_fasteners=["Metal welding", "Marine epoxy"],
        notes="Static light load allows simple nails. Vertical orientation "
              "and immediate use favor mechanical. Removable excludes permanent adhesives.",
    ),
    TestScenario(
        id="C04",
        name="Climbing Wall Hold Mounting",
        description="Mounting plastic climbing holds to plywood wall. Tension-dominant "
                    "loads as climbers pull on holds.",
        agent="C",
        answers={
            "material_a_type": "plastic",
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
            "access_one_side": False,
            "precision_required": False,
            "tension_dominant": True,
            "shock_loads": True,
        },
        expected_categories=["mechanical"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Hex bolt", "Lag bolt"],
        unexpected_fasteners=["Staple", "Brad nail", "Hot-melt glue"],
        notes="High tension + shock loads need strong mechanical fasteners. "
              "Removable constraint means no permanent adhesives. Bolts are standard for climbing walls.",
    ),
    TestScenario(
        id="C05",
        name="Overhead Ceiling Light Fixture",
        description="Mounting a heavy metal light fixture to ceiling. Overhead "
                    "installation, must never fall.",
        agent="C",
        answers={
            "material_a_type": "metal",
            "material_b_type": "masonry",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "permanent",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": True,
            "precision_required": True,
        },
        expected_categories=["mechanical"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Concrete screw", "Masonry nail"],
        unexpected_fasteners=["Hot-melt glue", "Fabric adhesive", "Duct tape"],
        notes="Overhead installation requires high shear strength - adhesives excluded. "
              "Safety-critical application demands robust mechanical anchoring.",
    ),
    TestScenario(
        id="C06",
        name="Precision Optical Instrument Mount",
        description="Mounting optical sensor to metal bracket. Requires precise "
                    "positioning that won't shift.",
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
        expected_categories=["mechanical", "thermal", "adhesive"],
        excluded_categories=[],
        expected_fasteners=["Dowel pin", "Two-component epoxy", "Metal epoxy"],
        unexpected_fasteners=["Hot-melt glue", "Duct tape"],
        notes="Precision positioning requires vibration resistance. Dowel pins "
              "provide precise alignment. High-quality epoxies maintain position.",
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT D: EDGE CASES AND CONSTRAINT COMBINATIONS
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_D_SCENARIOS = [
    TestScenario(
        id="D01",
        name="One-Sided Access Panel",
        description="Attaching access panel to enclosure where only exterior is "
                    "accessible. Cannot reach inside.",
        agent="D",
        answers={
            "material_a_type": "metal",
            "material_b_type": "metal",
            "environment_moisture": "none",
            "load_type": "static",
            "permanence": "removable",
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "immediate",
            "access_one_side": True,
            "precision_required": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Sheet metal screw", "rivet"],
        unexpected_fasteners=["Hex bolt", "Dowel pin"],
        notes="One-sided access excludes fasteners requiring two-sided access "
              "(like hex bolts with nuts). Self-tapping screws or blind rivets work.",
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
        expected_categories=["adhesive", "mechanical"],
        excluded_categories=["thermal"],
        expected_fasteners=["Wood glue (PVA)", "Staple"],
        unexpected_fasteners=["Metal welding", "Superglue (cyanoacrylate)", "Contact cement"],
        notes="Health constraints exclude thermal and toxic adhesives. PVA glue "
              "is non-toxic and standard for school projects. Staples are safe if supervised.",
    ),
    TestScenario(
        id="D03",
        name="Flexible Joint Requirement",
        description="Connecting two parts that need to flex relative to each other. "
                    "Like a hinge without being a hinge.",
        agent="D",
        answers={
            "material_a_type": "plastic",
            "material_b_type": "plastic",
            "environment_moisture": "none",
            "load_type": "light_dynamic",
            "vibration": False,
            "permanence": "permanent",
            "chemical_exposure": False,
            "flexibility_required": True,
            "orientation_vertical": False,
            "health_constraints": False,
            "max_curing_time": "moderate",
            "access_one_side": False,
            "precision_required": False,
            "tension_dominant": False,
            "shock_loads": False,
        },
        expected_categories=["adhesive"],
        excluded_categories=[],
        expected_fasteners=["Silicone sealant", "Contact cement"],
        unexpected_fasteners=["Two-component epoxy", "Metal welding", "Hex bolt"],
        notes="Flexibility required means only flexible/semi-flexible rigidity allowed. "
              "Rigid adhesives and mechanical fasteners won't work.",
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
            "tension_dominant": True,
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
        name="Immediate Curing Constraint",
        description="Emergency repair where joint must be usable immediately. "
                    "No time to wait for curing.",
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
        expected_categories=["mechanical"],
        excluded_categories=["adhesive"],
        expected_fasteners=["Wood screw", "Hex bolt"],
        unexpected_fasteners=["Two-component epoxy", "Polyurethane glue", "Marine epoxy"],
        notes="Immediate curing time excludes adhesives that need time to set. "
              "Mechanical fasteners provide instant holding power.",
    ),
    TestScenario(
        id="D07",
        name="Maximum Exclusion Stacking",
        description="Testing how multiple exclusion rules stack: outdoor + UV + "
                    "vibration + vertical.",
        agent="D",
        answers={
            "material_a_type": "wood",
            "material_b_type": "masonry",
            "environment_moisture": "outdoor",
            "load_type": "heavy_dynamic",
            "vibration": True,
            "permanence": "permanent",
            "uv_exposure": True,
            "temperature_extremes": True,
            "chemical_exposure": False,
            "flexibility_required": False,
            "orientation_vertical": True,
            "health_constraints": False,
            "max_curing_time": "slow",
            "access_one_side": True,
            "precision_required": False,
            "tension_dominant": True,
            "shock_loads": False,
        },
        expected_categories=["mechanical"],
        excluded_categories=["adhesive", "thermal"],
        expected_fasteners=["Lag bolt", "Concrete screw"],
        unexpected_fasteners=["Wood glue (PVA)", "Hot-melt glue", "Metal welding"],
        notes="Multiple exclusions stack: vibration excludes adhesive, "
              "vertical excludes adhesive, wood excludes thermal. "
              "Only robust mechanical fasteners remain.",
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
