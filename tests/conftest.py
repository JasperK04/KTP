"""Shared fixtures for the test suite"""
import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.engine import KnowledgeBase


@pytest.fixture
def kb_path():
    """Fixture to provide the path to kb.json"""
    return Path(__file__).parent.parent / "src" / "kb.json"


@pytest.fixture
def kb(kb_path):
    """Fixture to provide a loaded KnowledgeBase"""
    kb = KnowledgeBase()
    kb.load_from_file(str(kb_path))
    return kb


@pytest.fixture
def empty_kb():
    """Fixture to provide an empty KnowledgeBase"""
    return KnowledgeBase()
