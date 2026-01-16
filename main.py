import sys
from argparse import ArgumentParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app import create_app


def main():
    arg = ArgumentParser(description="Run the Flask web application.")
    arg.add_argument(
        "--debug",
        action="store_true",
        help="Run the Flask app in debug mode.",
    )
    arg.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port number to run the Flask app on.",
    )
    args = arg.parse_args()
    app = create_app()
    app.run(debug=args.debug, port=args.port)


if __name__ == "__main__":
    main()
