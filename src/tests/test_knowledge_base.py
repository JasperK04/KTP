"""Tests for KnowledgeBase loading, saving, and initialization"""
import pytest
import json
import tempfile
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import KnowledgeBase, Question, Fastener, Rule, SuggestionRule


class TestKnowledgeBaseInitialization:
    """Test suite for KnowledgeBase initialization"""
    
    def test_empty_initialization(self, empty_kb):
        """Test that a new KnowledgeBase initializes with empty collections"""
        assert empty_kb.fasteners == []
        assert empty_kb.rules == []
        assert empty_kb.questions == []
        assert empty_kb.suggestion_rules == []
    
    def test_initialization_creates_lists(self, empty_kb):
        """Test that initialization creates list objects (not None)"""
        assert isinstance(empty_kb.fasteners, list)
        assert isinstance(empty_kb.rules, list)
        assert isinstance(empty_kb.questions, list)
        assert isinstance(empty_kb.suggestion_rules, list)


class TestKnowledgeBaseLoading:
    """Test suite for KnowledgeBase loading from kb.json"""
    
    def test_kb_file_exists(self, kb_path):
        """Test that kb.json file exists"""
        assert kb_path.exists()
    
    def test_kb_loads_without_error(self, kb_path):
        """Test that KnowledgeBase can load without throwing an exception"""
        kb = KnowledgeBase()
        kb.load_from_file(str(kb_path))
        assert kb is not None
    
    def test_questions_loaded(self, kb):
        """Test that questions are loaded from kb.json"""
        assert len(kb.questions) > 0
        assert isinstance(kb.questions[0], Question)
    
    def test_fasteners_loaded(self, kb):
        """Test that fasteners are loaded from kb.json"""
        assert len(kb.fasteners) > 0
        assert isinstance(kb.fasteners[0], Fastener)
    
    def test_rules_loaded(self, kb):
        """Test that rules are loaded from kb.json"""
        assert len(kb.rules) > 0
        assert isinstance(kb.rules[0], Rule)
    
    def test_suggestion_rules_loaded(self, kb):
        """Test that suggestion rules are loaded from kb.json"""
        assert len(kb.suggestion_rules) > 0
        assert isinstance(kb.suggestion_rules[0], SuggestionRule)
    
    def test_correct_counts(self, kb):
        """Test that the correct number of items are loaded"""
        assert len(kb.questions) == 10
        assert len(kb.fasteners) == 7
        assert len(kb.rules) == 7
        assert len(kb.suggestion_rules) == 13
    
    def test_all_question_ids_present(self, kb):
        """Test that all expected question IDs are present"""
        expected_ids = [
            "material_type",
            "mechanical_strength",
            "moisture_exposure",
            "permanence",
            "curing_time",
            "load_type",
            "chemical_corrosion_resistance",
            "flexibility",
            "orientation",
            "health_concerns"
        ]
        actual_ids = [q.id for q in kb.questions]
        
        for expected_id in expected_ids:
            assert expected_id in actual_ids
    
    def test_all_fastener_names_present(self, kb):
        """Test that all expected fasteners are present"""
        expected_names = [
            "Wood glue (PVA)",
            "Two-component epoxy",
            "Silicone sealant",
            "Hex bolts with nuts",
            "Wood screws",
            "Metal welding",
            "Cable ties (zip-ties)"
        ]
        actual_names = [f.name for f in kb.fasteners]
        
        for expected_name in expected_names:
            assert expected_name in actual_names
    
    def test_all_rule_ids_present(self, kb):
        """Test that all expected rule IDs are present"""
        expected_ids = [
            "high_strength_metal",
            "waterproof_flexible",
            "removable_connection",
            "immediate_use",
            "wood_to_wood",
            "glass_ceramic_applications",
            "high_vibration"
        ]
        actual_ids = [r.id for r in kb.rules]
        
        for expected_id in expected_ids:
            assert expected_id in actual_ids


class TestKnowledgeBaseSaving:
    """Test suite for KnowledgeBase saving functionality"""
    
    def test_save_to_file(self, kb):
        """Test that KnowledgeBase can save to a file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            kb.save_to_file(temp_path)
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_and_reload(self, kb):
        """Test that saved KnowledgeBase can be reloaded correctly"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            kb.save_to_file(temp_path)
            
            kb2 = KnowledgeBase()
            kb2.load_from_file(temp_path)
            
            assert len(kb2.questions) == len(kb.questions)
            assert len(kb2.fasteners) == len(kb.fasteners)
            assert len(kb2.rules) == len(kb.rules)
            assert len(kb2.suggestion_rules) == len(kb.suggestion_rules)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_preserves_question_data(self, kb):
        """Test that saved questions preserve all data"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            kb.save_to_file(temp_path)
            kb2 = KnowledgeBase()
            kb2.load_from_file(temp_path)
            
            q1 = kb.questions[0]
            q2 = kb2.questions[0]
            
            assert q1.id == q2.id
            assert q1.text == q2.text
            assert q1.type == q2.type
            assert q1.choices == q2.choices
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_preserves_fastener_data(self, kb):
        """Test that saved fasteners preserve all data"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            kb.save_to_file(temp_path)
            kb2 = KnowledgeBase()
            kb2.load_from_file(temp_path)
            
            f1 = kb.fasteners[0]
            f2 = kb2.fasteners[0]
            
            assert f1.name == f2.name
            assert f1.category == f2.category
            assert f1.requires_tools == f2.requires_tools
            assert f1.surface_prep == f2.surface_prep
            assert f1.curing_time == f2.curing_time
            assert f1.properties.tensile_strength == f2.properties.tensile_strength
            assert f1.properties.compatible_materials == f2.properties.compatible_materials
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_preserves_rule_data(self, kb):
        """Test that saved rules preserve all data"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            kb.save_to_file(temp_path)
            kb2 = KnowledgeBase()
            kb2.load_from_file(temp_path)
            
            r1 = kb.rules[0]
            r2 = kb2.rules[0]
            
            assert r1.id == r2.id
            assert r1.conditions == r2.conditions
            assert r1.conclusion == r2.conclusion
            assert r1.priority == r2.priority
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_preserves_suggestion_rule_data(self, kb):
        """Test that saved suggestion rules preserve all data"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            kb.save_to_file(temp_path)
            kb2 = KnowledgeBase()
            kb2.load_from_file(temp_path)
            
            s1 = kb.suggestion_rules[0]
            s2 = kb2.suggestion_rules[0]
            
            assert s1.id == s2.id
            assert s1.applies_to_fasteners == s2.applies_to_fasteners
            assert s1.conditions == s2.conditions
            assert s1.suggestion == s2.suggestion
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_saved_json_is_valid(self, kb):
        """Test that the saved JSON is valid and can be parsed"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            kb.save_to_file(temp_path)
            
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            assert "questions" in data
            assert "fasteners" in data
            assert "rules" in data
            assert "suggestion_rules" in data
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
