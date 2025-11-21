from flask import Blueprint, abort, redirect, render_template, request, url_for

from app.utils import QUESTIONS

routes = Blueprint("app", __name__)


@routes.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@routes.route("/question", methods=["GET", "POST"])
def questions():
    questions = list(QUESTIONS.keys())
    if request.method == "POST":
        qid = request.form.get("answer")
        return redirect(url_for("app.question", qid=qid))
    return render_template("questions.html", questions=questions)


@routes.route("/question/<qid>", methods=["GET", "POST"])
def question(qid):
    data = QUESTIONS.get(qid)
    if not data:
        abort(404)
    selected = None
    if request.method == "POST":
        selected = request.form.get("answer")
    return render_template(
        "question.html",
        qid=qid,
        question=data["question"],
        options=data["options"],
        selected=selected,
    )
