from datetime import datetime
from pathlib import Path

from flask import Blueprint, redirect, render_template, request, session, url_for

from engine import InferenceEngine, KnowledgeBase, QuestionType

routes = Blueprint("routes", __name__)


def load_engine():
    kb_path = Path(__file__).resolve().parents[2] / "src" / "kb.json"
    kb = KnowledgeBase()
    kb.load_from_file(str(kb_path))

    engine = InferenceEngine(kb)

    if "facts" in session:
        engine.restore_facts(session["facts"])

    return engine


@routes.before_app_request
def ensure_session():
    session.setdefault("facts", {})
    session.setdefault("question_index", 0)
    session.setdefault("question_history", [])


@routes.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@routes.route("/question", methods=["GET", "POST"])
def question():
    engine = load_engine()
    questions = engine.kb.questions
    idx = session["question_index"]

    if idx >= len(questions):
        return redirect(url_for("routes.results"))

    question = questions[idx]

    if request.method == "POST":
        raw = request.form.get("answer")

        if raw != "skip":
            if question.type == QuestionType.BOOLEAN:
                value = raw
            elif question.type == QuestionType.CHOICE:
                value = raw
            else:
                value = None

            if value is not None:
                engine.add_fact(question.id, value)
                session["facts"] = engine.retrieve_facts()

        session["question_history"].append(
            {
                "question_id": question.id,
                "question_text": question.text,
                "answer": None if raw == "skip" else str(value),
                "timestamp": datetime.now().isoformat(),
            }
        )

        session["question_index"] += 1
        return redirect(url_for("routes.question"))

    return render_template(
        "question.html",
        question=question,
        index=idx + 1,
        total=len(questions),
        question_type=question.type.value,
    )


@routes.route("/results", methods=["GET"])
def results():
    engine = load_engine()
    recommendations = engine.recommend_fasteners()

    return render_template(
        "results.html",
        recommendations=recommendations,
        facts=session.get("facts", {}),
        history=session.get("question_history", []),
    )


@routes.route("/questions", methods=["GET"])
def questions_overview():
    engine = load_engine()
    recommendations = engine.recommend_fasteners()

    return render_template(
        "questions.html",
        history=session.get("question_history", []),
        facts=session.get("facts", {}),
        recommendations=recommendations,
    )


@routes.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect(url_for("routes.index"))
