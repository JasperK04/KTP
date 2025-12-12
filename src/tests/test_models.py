"""Tests for dataclass models (Question, Rule, Fastener, MaterialProperties, etc.)"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import (
    Question,
    Rule,
    SuggestionRule,
    Fastener,
    MaterialProperties,
    QuestionType,
    FastenerCategory,
    Strength,
    Resistance,
    Permanence,
    Rigidity
)


class TestQuestionModel:
    """Test suite for Question dataclass"""
    
    def test_question_instantiation(self):
        """Test that Question can be instantiated"""
        q = Question(
            id="test_id",
            text="Test question?",
            type=QuestionType.CHOICE,
            choices=["option1", "option2"]
        )
        assert q.id == "test_id"
        assert q.text == "Test question?"
        assert q.type == QuestionType.CHOICE
        assert q.choices == ["option1", "option2"]
    
    def test_question_to_dict(self):
        """Test Question serialization to dict"""
        q = Question(
            id="test_id",
            text="Test question?",
            type=QuestionType.BOOLEAN,
            choices=[]
        )
        d = q.to_dict()
        assert d["id"] == "test_id"
        assert d["text"] == "Test question?"
        assert d["answer_type"] == "boolean"
        assert d["choices"] == []
    
    def test_question_from_dict(self):
        """Test Question deserialization from dict"""
        data = {
            "id": "test_id",
            "text": "Test question?",
            "answer_type": "choice",
            "choices": ["a", "b", "c"]
        }
        q = Question.from_dict(data)
        assert q.id == "test_id"
        assert q.text == "Test question?"
        assert q.type == QuestionType.CHOICE
        assert q.choices == ["a", "b", "c"]
    
    def test_question_from_kb_json(self, kb):
        """Test that all questions from kb.json are valid"""
        for question in kb.questions:
            assert isinstance(question, Question)
            assert question.id
            assert question.text
            assert isinstance(question.type, QuestionType)
            
            if question.type == QuestionType.CHOICE:
                assert len(question.choices) > 0
            else:
                assert len(question.choices) == 0


class TestMaterialPropertiesModel:
    """Test suite for MaterialProperties dataclass"""
    
    def test_material_properties_instantiation(self):
        """Test that MaterialProperties can be instantiated"""
        props = MaterialProperties(
            compatible_materials=["wood", "metal"],
            tensile_strength=Strength.HIGH,
            shear_strength=Strength.MODERATE,
            compressive_strength=Strength.HIGH,
            water_resistance=Resistance.GOOD,
            weather_resistance=Resistance.GOOD,
            chemical_resistance=Resistance.FAIR,
            temperature_resistance=Resistance.EXCELLENT,
            vibration_resistance=Resistance.GOOD,
            rigidity=Rigidity.RIGID,
            permanence=Permanence.PERMANENT,
            notes=["Test note"]
        )
        assert props.compatible_materials == ["wood", "metal"]
        assert props.tensile_strength == Strength.HIGH
        assert props.rigidity == Rigidity.RIGID
    
    def test_material_properties_to_dict(self):
        """Test MaterialProperties serialization"""
        props = MaterialProperties(
            compatible_materials=["wood"],
            tensile_strength=Strength.LOW,
            shear_strength=Strength.LOW,
            compressive_strength=Strength.LOW,
            water_resistance=Resistance.POOR,
            weather_resistance=Resistance.POOR,
            chemical_resistance=Resistance.POOR,
            temperature_resistance=Resistance.FAIR,
            vibration_resistance=Resistance.POOR,
            rigidity=Rigidity.FLEXIBLE,
            permanence=Permanence.REMOVABLE,
            notes=[]
        )
        d = props.to_dict()
        assert d["compatible_materials"] == ["wood"]
        assert d["tensile_strength"] == "low"
        assert d["rigidity"] == "flexible"
    
    def test_material_properties_from_dict(self):
        """Test MaterialProperties deserialization"""
        data = {
            "compatible_materials": ["metal"],
            "tensile_strength": "very_high",
            "shear_strength": "very_high",
            "compressive_strength": "very_high",
            "water_resistance": "excellent",
            "weather_resistance": "excellent",
            "chemical_resistance": "excellent",
            "temperature_resistance": "excellent",
            "vibration_resistance": "excellent",
            "rigidity": "rigid",
            "permanence": "permanent",
            "notes": ["Test"]
        }
        props = MaterialProperties.from_dict(data)
        assert props.compatible_materials == ["metal"]
        assert props.tensile_strength == Strength.VERY_HIGH
        assert props.permanence == Permanence.PERMANENT


class TestFastenerModel:
    """Test suite for Fastener dataclass"""
    
    def test_fastener_instantiation(self):
        """Test that Fastener can be instantiated"""
        props = MaterialProperties(
            compatible_materials=["wood"],
            tensile_strength=Strength.MODERATE,
            shear_strength=Strength.MODERATE,
            compressive_strength=Strength.LOW,
            water_resistance=Resistance.POOR,
            weather_resistance=Resistance.POOR,
            chemical_resistance=Resistance.POOR,
            temperature_resistance=Resistance.FAIR,
            vibration_resistance=Resistance.POOR,
            rigidity=Rigidity.RIGID,
            permanence=Permanence.SEMI_PERMANENT
        )
        
        fastener = Fastener(
            name="Test Fastener",
            category=FastenerCategory.ADHESIVE,
            properties=props,
            requires_tools=["tool1"],
            surface_prep=["clean"],
            curing_time="1 hour",
            special_conditions=[]
        )
        
        assert fastener.name == "Test Fastener"
        assert fastener.category == FastenerCategory.ADHESIVE
        assert fastener.requires_tools == ["tool1"]
    
    def test_fastener_to_dict(self):
        """Test Fastener serialization"""
        props = MaterialProperties(
            compatible_materials=["wood"],
            tensile_strength=Strength.MODERATE,
            shear_strength=Strength.MODERATE,
            compressive_strength=Strength.LOW,
            water_resistance=Resistance.POOR,
            weather_resistance=Resistance.POOR,
            chemical_resistance=Resistance.POOR,
            temperature_resistance=Resistance.FAIR,
            vibration_resistance=Resistance.POOR,
            rigidity=Rigidity.RIGID,
            permanence=Permanence.SEMI_PERMANENT
        )
        
        fastener = Fastener(
            name="Test",
            category=FastenerCategory.MECHANICAL,
            properties=props
        )
        
        d = fastener.to_dict()
        assert d["name"] == "Test"
        assert d["category"] == "mechanical"
        assert "properties" in d
    
    def test_fastener_from_dict(self):
        """Test Fastener deserialization"""
        data = {
            "name": "Test Fastener",
            "category": "thermal",
            "properties": {
                "compatible_materials": ["metal"],
                "tensile_strength": "high",
                "shear_strength": "high",
                "compressive_strength": "high",
                "water_resistance": "good",
                "weather_resistance": "good",
                "chemical_resistance": "good",
                "temperature_resistance": "excellent",
                "vibration_resistance": "good",
                "rigidity": "rigid",
                "permanence": "permanent",
                "notes": []
            },
            "requires_tools": ["welder"],
            "surface_prep": ["clean"],
            "curing_time": "immediate",
            "special_conditions": []
        }
        
        fastener = Fastener.from_dict(data)
        assert fastener.name == "Test Fastener"
        assert fastener.category == FastenerCategory.THERMAL
        assert fastener.properties.tensile_strength == Strength.HIGH
    
    def test_all_fasteners_from_kb_json(self, kb):
        """Test that all fasteners from kb.json are valid"""
        assert len(kb.fasteners) == 7
        
        expected_fasteners = [
            "Wood glue (PVA)",
            "Two-component epoxy",
            "Silicone sealant",
            "Hex bolts with nuts",
            "Wood screws",
            "Metal welding",
            "Cable ties (zip-ties)"
        ]
        
        for fastener in kb.fasteners:
            assert isinstance(fastener, Fastener)
            assert fastener.name in expected_fasteners
            assert isinstance(fastener.category, FastenerCategory)
            assert isinstance(fastener.properties, MaterialProperties)
            assert isinstance(fastener.requires_tools, list)
            assert isinstance(fastener.surface_prep, list)


class TestRuleModel:
    """Test suite for Rule dataclass"""
    
    def test_rule_instantiation(self):
        """Test that Rule can be instantiated"""
        rule = Rule(
            id="test_rule",
            conditions={"material_type": "wood"},
            conclusion={"recommended_categories": ["adhesive"]},
            priority=5
        )
        assert rule.id == "test_rule"
        assert rule.conditions == {"material_type": "wood"}
        assert rule.priority == 5
    
    def test_rule_to_dict(self):
        """Test Rule serialization"""
        rule = Rule(
            id="test_rule",
            conditions={"material_type": "wood"},
            conclusion={"recommended_categories": ["adhesive"]},
            priority=5
        )
        d = rule.to_dict()
        assert d["id"] == "test_rule"
        assert d["conditions"] == {"material_type": "wood"}
        assert d["priority"] == 5
    
    def test_rule_from_dict(self):
        """Test Rule deserialization"""
        data = {
            "id": "test_rule",
            "conditions": {"material_type": "metal"},
            "conclusion": {"recommended_categories": ["mechanical"]},
            "priority": 10
        }
        rule = Rule.from_dict(data)
        assert rule.id == "test_rule"
        assert rule.conditions["material_type"] == "metal"
    
    def test_all_rules_from_kb_json(self, kb):
        """Test that all rules from kb.json are valid"""
        assert len(kb.rules) == 7
        
        expected_rule_ids = [
            "high_strength_metal",
            "waterproof_flexible",
            "removable_connection",
            "immediate_use",
            "wood_to_wood",
            "glass_ceramic_applications",
            "high_vibration"
        ]
        
        for rule in kb.rules:
            assert isinstance(rule, Rule)
            assert rule.id in expected_rule_ids
            assert isinstance(rule.conditions, dict)
            assert isinstance(rule.conclusion, dict)
            assert isinstance(rule.priority, int)


class TestSuggestionRuleModel:
    """Test suite for SuggestionRule dataclass"""
    
    def test_suggestion_rule_instantiation(self):
        """Test that SuggestionRule can be instantiated"""
        rule = SuggestionRule(
            id="test_suggestion",
            applies_to_fasteners=["bolts"],
            conditions={"moisture_exposure": "outdoor"},
            suggestion="Use stainless steel"
        )
        assert rule.id == "test_suggestion"
        assert rule.applies_to_fasteners == ["bolts"]
        assert rule.suggestion == "Use stainless steel"
    
    def test_suggestion_rule_to_dict(self):
        """Test SuggestionRule serialization"""
        rule = SuggestionRule(
            id="test_suggestion",
            applies_to_fasteners=["all"],
            conditions={},
            suggestion="Test suggestion"
        )
        d = rule.to_dict()
        assert d["id"] == "test_suggestion"
        assert d["applies_to_fasteners"] == ["all"]
        assert d["suggestion"] == "Test suggestion"
    
    def test_suggestion_rule_from_dict(self):
        """Test SuggestionRule deserialization"""
        data = {
            "id": "test_suggestion",
            "applies_to_fasteners": ["screws"],
            "conditions": {"material_type": "wood"},
            "suggestion": "Pre-drill pilot holes"
        }
        rule = SuggestionRule.from_dict(data)
        assert rule.id == "test_suggestion"
        assert rule.applies_to_fasteners == ["screws"]
        assert rule.suggestion == "Pre-drill pilot holes"
    
    def test_all_suggestion_rules_from_kb_json(self, kb):
        """Test that all suggestion rules from kb.json are valid"""
        assert len(kb.suggestion_rules) == 13
        
        for suggestion_rule in kb.suggestion_rules:
            assert isinstance(suggestion_rule, SuggestionRule)
            assert suggestion_rule.id
            assert isinstance(suggestion_rule.applies_to_fasteners, list)
            assert len(suggestion_rule.applies_to_fasteners) > 0
            assert isinstance(suggestion_rule.conditions, dict)
            assert suggestion_rule.suggestion
            assert isinstance(suggestion_rule.suggestion, str)
