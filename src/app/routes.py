import json
from pathlib import Path

from flask import Blueprint, redirect, render_template, request, session, url_for

from domain_model import FasteningTask
from input_model import InputModel
from rule_model import ForwardChainingEngine, RuleFactory
from solving_model import ProblemSolvingModel

routes = Blueprint("routes", __name__)


# ─────────────────────────────────────────────
# INITIALIZATION
# ─────────────────────────────────────────────


def load_kb():
    kb_path = Path(__file__).resolve().parents[2] / "src" / "kb.json"
    with open(kb_path, "r") as f:
        return json.load(f)


def load_models():
    kb = load_kb()

    input_model = InputModel(kb["questions"], kb["materials"])

    rule_factory = RuleFactory(kb["rules"])
    rule_engine = ForwardChainingEngine(rule_factory.build_rule_base())

    problem_solver = ProblemSolvingModel(
        rule_engine=rule_engine,
        fasteners=[  # load from KB
            f
            for f in map(
                lambda x: __import__("domain_model").Fastener.from_dict(x),
                kb["fasteners"],
            )
        ],
    )

    if "input_state" in session:
        input_model.restore_state(session["input_state"])

    task_state = session.get("task_state")
    if task_state and "materials" in task_state:
        input_model.task = FasteningTask.from_dict(task_state)

    if "engine_state" in session:
        rule_engine.restore_state(session["engine_state"])

    return input_model, rule_engine, problem_solver


@routes.before_app_request
def ensure_session():
    session.setdefault("input_state", {})
    session.setdefault("task_state", {})
    session.setdefault("engine_state", {})


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────


@routes.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────
# QUESTION ROUTE
# ─────────────────────────────────────────────


@routes.route("/question", methods=["GET", "POST"])
def question():
    input_model, rule_engine, _ = load_models()

    question = input_model.get_next_question()
    if question is None:
        return redirect(url_for("routes.results"))

    if request.method == "POST":
        value = request.form.get("answer")
        if value is not None:
            input_model.answer_question(question["id"], value)

            session["input_state"] = input_model.get_state()
            session["task_state"] = input_model.get_task().to_dict()

        return redirect(url_for("routes.question"))

    explanation_ids = input_model.get_question_explanation(question["id"])
    contexts = [
        rule.context
        for rule in rule_engine.rule_base.rules
        if rule.id in explanation_ids
    ]

    explanations = []
    for explanation_id, contexts in zip(explanation_ids, contexts):
        explanations.append(
            f"{explanation_id.replace('_', ' ').capitalize()}: {contexts}"
        )

    return render_template(
        "question.html",
        question=question,
        explanations=explanations,
    )


# ─────────────────────────────────────────────
# QUESTIONS OVERVIEW (INTERNAL STATE)
# ─────────────────────────────────────────────


@routes.route("/questions", methods=["GET"])
def questions_overview():
    input_model, rule_engine, _ = load_models()

    return render_template(
        "questions.html",
        answers=input_model.answers,
        task=input_model.get_task().to_dict(),
        fired_rules=list(rule_engine.fired_rules),
    )


# ─────────────────────────────────────────────
# RESULTS ROUTE (FINAL CONCLUSION)
# ─────────────────────────────────────────────


@routes.route("/results", methods=["GET"])
def results():
    input_model, rule_engine, solver = load_models()

    task = input_model.get_task()
    recommendations = solver.recommend(task)

    session["engine_state"] = rule_engine.get_state()
    session["task_state"] = task.to_dict()

    return render_template(
        "results.html",
        recommendations=recommendations,
        task=task.to_dict(),
        fired_rules=list(rule_engine.fired_rules),
    )


# ─────────────────────────────────────────────
# RESET
# ─────────────────────────────────────────────


@routes.route("/reset", methods=["GET", "POST"])
def reset():
    session.clear()
    return redirect(url_for("routes.index"))
