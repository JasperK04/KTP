from os import getenv

from flask import Flask
from flask_session import Session

from src.app.config import config
from src.app.routes import routes


def create_app():
    app = Flask(__name__)
    environment = getenv("ENV", "development")
    app.config.from_object(config[environment])
    app.register_blueprint(routes)
    Session(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
