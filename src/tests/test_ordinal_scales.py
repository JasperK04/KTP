"""Tests for OrdinalScales and enum ordering logic"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import OrdinalScales, Strength, Resistance


class TestOrdinalScales:
    """Test suite for OrdinalScales class"""
    
    def test_strength_scale_exists(self):
        """Test that STRENGTH scale is defined"""
        assert hasattr(OrdinalScales, 'STRENGTH')
        assert isinstance(OrdinalScales.STRENGTH, list)
    
    def test_strength_scale_content(self):
        """Test that STRENGTH scale has correct values"""
        expected = ["none", "very_low", "low", "moderate", "high", "very_high"]
        assert OrdinalScales.STRENGTH == expected
    
    def test_strength_scale_ordering(self):
        """Test that STRENGTH scale is ordered from weakest to strongest"""
        scale = OrdinalScales.STRENGTH
        assert scale.index("none") < scale.index("very_low")
        assert scale.index("very_low") < scale.index("low")
        assert scale.index("low") < scale.index("moderate")
        assert scale.index("moderate") < scale.index("high")
        assert scale.index("high") < scale.index("very_high")
    
    def test_resistance_scale_exists(self):
        """Test that RESISTANCE scale is defined"""
        assert hasattr(OrdinalScales, 'RESISTANCE')
        assert isinstance(OrdinalScales.RESISTANCE, list)
    
    def test_resistance_scale_content(self):
        """Test that RESISTANCE scale has correct values"""
        expected = ["poor", "fair", "good", "excellent"]
        assert OrdinalScales.RESISTANCE == expected
    
    def test_resistance_scale_ordering(self):
        """Test that RESISTANCE scale is ordered from worst to best"""
        scale = OrdinalScales.RESISTANCE
        assert scale.index("poor") < scale.index("fair")
        assert scale.index("fair") < scale.index("good")
        assert scale.index("good") < scale.index("excellent")
    
    def test_moisture_to_resistance_mapping_exists(self):
        """Test that MOISTURE_TO_RESISTANCE mapping is defined"""
        assert hasattr(OrdinalScales, 'MOISTURE_TO_RESISTANCE')
        assert isinstance(OrdinalScales.MOISTURE_TO_RESISTANCE, dict)
    
    def test_moisture_to_resistance_mapping_content(self):
        """Test that MOISTURE_TO_RESISTANCE has correct mappings"""
        expected = {
            "no": "poor",
            "splash": "fair",
            "outdoor": "good",
            "submerged": "excellent"
        }
        assert OrdinalScales.MOISTURE_TO_RESISTANCE == expected
    
    def test_moisture_to_resistance_mapping_is_ordinal(self):
        """Test that moisture exposure requirements increase ordinally"""
        mapping = OrdinalScales.MOISTURE_TO_RESISTANCE
        scale = OrdinalScales.RESISTANCE
        
        # Each higher moisture exposure should require equal or higher resistance
        no_idx = scale.index(mapping["no"])
        splash_idx = scale.index(mapping["splash"])
        outdoor_idx = scale.index(mapping["outdoor"])
        submerged_idx = scale.index(mapping["submerged"])
        
        assert no_idx <= splash_idx
        assert splash_idx <= outdoor_idx
        assert outdoor_idx <= submerged_idx


class TestStrengthEnum:
    """Test suite for Strength enum"""
    
    def test_strength_enum_values(self):
        """Test that Strength enum has all expected values"""
        assert Strength.NONE.value == "none"
        assert Strength.VERY_LOW.value == "very_low"
        assert Strength.LOW.value == "low"
        assert Strength.MODERATE.value == "moderate"
        assert Strength.HIGH.value == "high"
        assert Strength.VERY_HIGH.value == "very_high"
    
    def test_strength_enum_from_string(self):
        """Test that Strength enum can be created from string value"""
        assert Strength("none") == Strength.NONE
        assert Strength("high") == Strength.HIGH
        assert Strength("very_high") == Strength.VERY_HIGH


class TestResistanceEnum:
    """Test suite for Resistance enum"""
    
    def test_resistance_enum_values(self):
        """Test that Resistance enum has all expected values"""
        assert Resistance.POOR.value == "poor"
        assert Resistance.FAIR.value == "fair"
        assert Resistance.GOOD.value == "good"
        assert Resistance.EXCELLENT.value == "excellent"
    
    def test_resistance_enum_from_string(self):
        """Test that Resistance enum can be created from string value"""
        assert Resistance("poor") == Resistance.POOR
        assert Resistance("good") == Resistance.GOOD
        assert Resistance("excellent") == Resistance.EXCELLENT


class TestOrdinalComparisons:
    """Test suite for ordinal comparison logic"""
    
    def test_strength_comparison_meets_requirement(self):
        """Test that higher strength values meet lower requirements"""
        scale = OrdinalScales.STRENGTH
        
        required = "moderate"
        actual = "high"
        
        req_idx = scale.index(required)
        actual_idx = scale.index(actual)
        
        assert actual_idx >= req_idx
    
    def test_strength_comparison_fails_requirement(self):
        """Test that lower strength values don't meet higher requirements"""
        scale = OrdinalScales.STRENGTH
        
        required = "high"
        actual = "low"
        
        req_idx = scale.index(required)
        actual_idx = scale.index(actual)
        
        assert actual_idx < req_idx
    
    def test_resistance_comparison_meets_requirement(self):
        """Test that higher resistance values meet lower requirements"""
        scale = OrdinalScales.RESISTANCE
        
        required = "fair"
        actual = "excellent"
        
        req_idx = scale.index(required)
        actual_idx = scale.index(actual)
        
        assert actual_idx >= req_idx
    
    def test_resistance_comparison_fails_requirement(self):
        """Test that lower resistance values don't meet higher requirements"""
        scale = OrdinalScales.RESISTANCE
        
        required = "excellent"
        actual = "poor"
        
        req_idx = scale.index(required)
        actual_idx = scale.index(actual)
        
        assert actual_idx < req_idx
