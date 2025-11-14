import json
import sys
from pathlib import Path

def load_json(path: Path) -> dict | None:
    """
    Read JSON from a file and print the loaded object.
    Usage: python main.py [path_to_json]
    If no path is provided, defaults to 'data.json' in the current directory.
    """
    path = Path(sys.argv[1])
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON in {path}: {e}")
        return None
    return data


def parse_args_to_path() -> Path:
    # require exactly one argument (script name + one path)
    if len(sys.argv) != 2:
        raise ValueError("Expected exactly one argument: path to JSON file")

    raw = sys.argv[1]
    # ensure the argument is a string-like value
    if not isinstance(raw, str):
        raise TypeError("Path argument must be a string")

    if raw.strip() == "":
        raise ValueError("Path argument is empty")

    try:
        path = Path(raw)
    except Exception as e:
        raise ValueError(f"Failed to parse path '{raw}' into Path: {e}") from e

    return path

def main():
    path = parse_args_to_path()
    json_data = load_json(path)
    if json_data:
        for key, value in json_data.items():
            print(f"{key:<8}: {value}")

if __name__ == "__main__":
    main()
