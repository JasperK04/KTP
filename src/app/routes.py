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
    session.setdefault("count", 1)
    session.setdefault("question_history", [])


@routes.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@routes.route("/question", methods=["GET", "POST"])
def question():
    engine = load_engine()

    asked = {h["question_id"] for h in session["question_history"]}
    question = engine.select_next_question(asked)

    if question is None:
        return redirect(url_for("routes.results"))

    if request.method == "POST":
        raw = request.form.get("answer")
        if not raw:
            return redirect(url_for("routes.question"))
        session["count"] += 1

        if raw != "skip":
            if question.type == QuestionType.BOOLEAN:
                raw = raw.lower() in ["true", "yes", "y"]

            engine.add_fact(question.id, raw)
            session["facts"] = engine.retrieve_facts()

        session["question_history"].append(
            {
                "question_id": question.id,
                "question_text": question.text,
                "answer": None if raw == "skip" else raw,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return redirect(url_for("routes.question"))

    return render_template(
        "question.html",
        question=question,
        count=session["count"],
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
