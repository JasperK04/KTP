from os import getenv

from flask import Flask

from app.config import config
from app.routes import routes


def create_app():
    app = Flask(__name__)
    environment = getenv("ENV", "development")
    app.config.from_object(config[environment])
    app.register_blueprint(routes)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
