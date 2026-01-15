"""Shared fixtures for the test suite"""
import json
import sys
from pathlib import Path

import pytest

# Add src directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from domain_model import Fastener
from input_model import InputModel
from rule_model import ForwardChainingEngine, RuleFactory


@pytest.fixture
def kb_path():
    """Fixture to provide the path to kb.json"""
    return Path(__file__).parent.parent / "src" / "kb.json"


@pytest.fixture
def kb_data(kb_path):
    """Fixture to provide the raw dictionary content of kb.json"""
    if not kb_path.exists():
        pytest.fail(f"Knowledge base file not found at: {kb_path}")
    
    with open(kb_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def loaded_fasteners(kb_data):
    """Fixture to provide the list of Fastener objects loaded from kb.json"""
    return [Fastener.from_dict(f) for f in kb_data["fasteners"]]


@pytest.fixture
def loaded_input_model(kb_data):
    """Fixture to provide an InputModel initialized with real questions"""
    return InputModel(kb_data["questions"])


@pytest.fixture
def loaded_rule_engine(kb_data):
    """Fixture to provide a ForwardChainingEngine loaded with real rules"""
    factory = RuleFactory(kb_data["rules"])
    return ForwardChainingEngine(factory.build_rule_base())