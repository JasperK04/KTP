import re
from pathlib import Path


def main():
    text = Path("pyproject.toml").read_text()

    block = re.search(r"dependencies\s*=\s*\[(.*?)\]", text, re.S)
    deps = re.findall(r'"([^"]+)"', block.group(1)) if block else []

    Path("requirements.txt").write_text("\n".join(deps))


if __name__ == "__main__":
    main()
