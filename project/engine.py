from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

# -----------------------------------------------
# ENUM classes
# -----------------------------------------------

class Strength(Enum):
    ...

class Resistance(Enum):
    ...

class Permanance(Enum):
    ...

class Rigidity(Enum):
    ...

# -----------------------------------------------
# Dataclasses
# -----------------------------------------------

@dataclass
class Question:
    """
    Docstring for Question
    """
    ...

@dataclass
class Rule:
    """
    Docstring for Rule
    """
    ...

@dataclass
class Fact:
    """
    Docstring for Fact
    """
    ...

@dataclass
class MaterialProperties:
    """
    Docstring for MaterialProperties
    """
    ...

@dataclass
class Fastener:
    """
    Docstring for Fastener
    """
    ...

# -----------------------------------------------
# Inference Engine
# -----------------------------------------------

class KnowledgeBase:
    """
    Docstring for KnowledgeBase
    """
    ...


class InferenceEngine:
    """
    Docstring for InferenceEngine
    """
    ...

