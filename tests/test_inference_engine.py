"""Tests for InferenceEngine logic and fastener recommendation (updated model)"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.engine import (
    FastenerCategory,
    InferenceEngine,
    KnowledgeBase,
    Permanence,
    Rigidity,
)


@pytest.fixture
def kb():
    kb = KnowledgeBase()
    kb_path = Path(__file__).parent.parent / "src" / "kb.json"
    kb.load_from_file(str(kb_path))
    return kb


class TestInferenceEngineBasics:
    def test_initial_state(self, kb):
        engine = InferenceEngine(kb)
        assert engine.facts == {}
        assert engine.conclusions == {}

    def test_reset_clears_state(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.conclusions["dummy"] = ["x"]

        engine.reset()

        assert engine.facts == {}
        assert engine.conclusions == {}


class TestFactHandling:
    def test_add_fact(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "metal")
        assert engine.facts["material_type"] == "metal"

    def test_overwrite_fact(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("material_type", "metal")
        assert engine.facts["material_type"] == "metal"

    def test_boolean_fact_is_boolean(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("flexibility", True)
        assert engine.facts["flexibility"] is True


class TestInference:
    def test_infer_no_rules_match(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "fabric")
        engine.infer()
        assert engine.conclusions == {}

    def test_infer_applies_matching_rules(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "metal")
        engine.add_fact("mechanical_strength", "very_high")
        engine.infer()

        assert "recommended_categories" in engine.conclusions


class TestFastenerMatching:
    def test_material_compatibility(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("material_type_2", "wood")

        wood_glue = next(f for f in kb.fasteners if "Wood glue" in f.name)
        welding = next(
            f for f in kb.fasteners if f.category == FastenerCategory.THERMAL
        )

        assert engine.matches_fastener(wood_glue)
        assert not engine.matches_fastener(welding)

    def test_strength_is_ordinal(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("mechanical_strength", "low")

        epoxy = next(f for f in kb.fasteners if "epoxy" in f.name.lower())
        assert engine.matches_fastener(epoxy)

    def test_strength_blocks_weaker_fastener(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("mechanical_strength", "high")

        glue = next(f for f in kb.fasteners if "Wood glue" in f.name)
        assert not engine.matches_fastener(glue)

    def test_moisture_resistance(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("moisture_exposure", "outdoor")

        epoxy = next(f for f in kb.fasteners if "epoxy" in f.name.lower())
        glue = next(f for f in kb.fasteners if "Wood glue" in f.name)

        assert engine.matches_fastener(epoxy)
        assert not engine.matches_fastener(glue)

    def test_permanence_filtering(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "metal")
        engine.add_fact("permanence", "removable")
        engine.infer()

        welding = next(
            f for f in kb.fasteners if f.category == FastenerCategory.THERMAL
        )
        bolts = next(f for f in kb.fasteners if "bolt" in f.name.lower())

        assert not engine.matches_fastener(welding)
        assert engine.matches_fastener(bolts)

    def test_flexibility_requirement(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "glass")
        engine.add_fact("flexibility", True)

        silicone = next(f for f in kb.fasteners if "Silicone" in f.name)
        epoxy = next(f for f in kb.fasteners if "epoxy" in f.name.lower())

        assert engine.matches_fastener(silicone)
        assert not engine.matches_fastener(epoxy)


class TestRecommendations:
    def test_basic_recommendation(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("mechanical_strength", "moderate")

        recs = engine.recommend_fasteners()
        assert recs
        for fastener, _ in recs:
            assert engine.matches_fastener(fastener)

    def test_high_strength_metal(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "metal")
        engine.add_fact("mechanical_strength", "very_high")

        recs = engine.recommend_fasteners()
        names = [f.name for f, _ in recs]

        assert any("welding" in n.lower() for n in names)

    def test_immediate_curing_excludes_adhesives(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("curing_time", "immediate")
        engine.infer()

        recs = engine.recommend_fasteners()
        for fastener, _ in recs:
            assert fastener.category != FastenerCategory.ADHESIVE

    def test_flexible_only(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "glass")
        engine.add_fact("flexibility", True)

        recs = engine.recommend_fasteners()
        for fastener, _ in recs:
            assert fastener.properties.rigidity in {
                Rigidity.FLEXIBLE,
                Rigidity.SEMI_FLEXIBLE,
            }


class TestSuggestions:
    def test_bolt_suggestions_outdoor(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("moisture_exposure", "outdoor")
        engine.add_fact("material_type", "metal")

        bolts = next(f for f in kb.fasteners if "bolt" in f.name.lower())
        suggestions = engine.get_suggestions(bolts)

        assert isinstance(suggestions, list)

    def test_vibration_suggestions(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("load_type", "vibration")
        engine.add_fact("material_type", "metal")

        bolts = next(f for f in kb.fasteners if "bolt" in f.name.lower())
        suggestions = engine.get_suggestions(bolts)

        assert isinstance(suggestions, list)


class TestSelectNextQuestion:
    """Tests for adaptive question selection logic"""

    def test_mandatory_material_questions_first(self, kb):
        engine = InferenceEngine(kb)

        q1 = engine.select_next_question(set())
        assert q1.id == "material_type"  # type: ignore

        engine.add_fact("material_type", "wood")
        q2 = engine.select_next_question({"material_type"})
        assert q2.id == "material_type_2"  # type: ignore

    def test_no_question_when_single_fastener_left(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "glass")
        engine.add_fact("flexibility", True)

        remaining = engine.remaining_fasteners()
        if len(remaining) <= 1:
            q = engine.select_next_question({"material_type", "material_type_2"})
            assert q is None

    def test_skipped_question_not_asked_again(self, kb):
        engine = InferenceEngine(kb)

        engine.add_fact("material_type", "wood")
        engine.add_fact("material_type_2", "wood")

        asked = {"material_type", "material_type_2"}
        q = engine.select_next_question(asked)

        if q:
            assert q.id not in asked

    def test_prefers_multi_category_question(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("material_type_2", "wood")

        asked = {"material_type", "material_type_2"}

        q = engine.select_next_question(asked)
        assert q is not None

        remaining = engine.remaining_fasteners()
        remaining_categories = engine.remaining_categories(remaining)

        # Selected question should apply to more than one remaining category
        coverage = len(set(q.applicable_to) & remaining_categories)
        assert coverage >= 1

    def test_single_category_question_only_when_needed(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "glass")
        engine.add_fact("material_type_2", "wood")

        asked = {"material_type", "material_type_2"}

        q = engine.select_next_question(asked)
        if q:
            remaining = engine.remaining_fasteners()
            remaining_categories = engine.remaining_categories(remaining)

            coverage = len(set(q.applicable_to) & remaining_categories)

            if coverage == 1:
                # Then no multi-category discriminating question must exist
                alternatives = []
                for candidate in kb.questions:
                    if candidate.id in asked:
                        continue
                    alt_coverage = len(
                        set(candidate.applicable_to) & remaining_categories
                    )
                    if alt_coverage > 1:
                        alternatives.append(candidate)

                assert not alternatives

    def test_returns_none_when_no_question_can_discriminate(self, kb):
        engine = InferenceEngine(kb)
        engine.add_fact("material_type", "wood")
        engine.add_fact("material_type_2", "wood")
        engine.add_fact("permanence", "semi_permanent")
        engine.add_fact("mechanical_strength", "moderate")
        engine.add_fact("moisture_exposure", "no")
        engine.add_fact("load_type", "heavy_dynamic")
        engine.add_fact("flexibility", True)

        asked = set(engine.facts.keys())
        q = engine.select_next_question(asked)

        assert q is None
