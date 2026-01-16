import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from src.domain_model import MaterialType
from src.input_model import InputModel

MATERIAL = [
    {
        "material_type": "wood",
        "porosity": "high",
        "brittleness": "low",
        "base_strength": "moderate",
    }
]


class TestInputModel:
    def test_get_next_question(self):
        questions = [
            {
                "id": "q1",
                "text": "Q1",
                "attribute": "materials.material_a.material_type",
                "type": "enum",
                "options": [],
            },
            {
                "id": "q2",
                "text": "Q2",
                "attribute": "environment.moisture",
                "type": "enum",
                "options": [],
            },
        ]
        model = InputModel(questions, MATERIAL)

        # Should get first question
        q = model.get_next_question()
        assert q["id"] == "q1"

        # Answer it
        model.answer_question("q1", "wood")

        # Should get second question
        q = model.get_next_question()
        assert q["id"] == "q2"

    def test_answer_updates_task(self):
        questions = [
            {
                "id": "q1",
                "text": "Mat?",
                "attribute": "materials.material_a.material_type",
                "type": "enum",
                "options": [],
            }
        ]
        model = InputModel(questions, MATERIAL)

        model.answer_question("q1", "wood")

        assert model.task.materials.material_a.material_type == MaterialType.WOOD
