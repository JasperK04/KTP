import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict

"""
/home/jasper/KTP/week2/rule_parser.py

Usage:
    python rule_parser.py <basename> <txt|json>

If <txt> is requested, this script reads <basename>.json and writes <basename>.txt
with lines like:
    IF <key> THEN <value>

If <json> is requested, this script reads <basename>.txt (lines like above) and
writes <basename>.json (a JSON object). Duplicate IF keys become lists of values.
"""

_IFTHEN_RE = re.compile(r"^\s*IF\s+(.+?)\s+THEN\s+(.+?)\s*$", flags=re.IGNORECASE)


def json_to_if_then(json_path: Path, out_txt_path: Path) -> None:
    json_path = Path(json_path)
    out_txt_path = Path(out_txt_path)

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    if isinstance(data, dict):
        items = data.items()
    elif isinstance(data, list):
        items = []
        for elem in data:
            if isinstance(elem, dict):
                # dicts with single key are treated as key->value, otherwise look for 'if'/'then'
                if len(elem) == 1:
                    k, v = next(iter(elem.items()))
                    items.append((k, v))
                elif "if" in elem and "then" in elem:
                    items.append((elem["if"], elem["then"]))
                else:
                    raise ValueError(f"Unrecognized list element structure: {elem!r}")
            elif isinstance(elem, (list, tuple)) and len(elem) == 2:
                items.append((elem[0], elem[1]))
            else:
                raise ValueError(f"Unrecognized list element: {elem!r}")
    else:
        raise ValueError("JSON root must be an object or a list of rules")

    for k, v in items:
        # Serialize complex values to JSON string so they round-trip sensibly
        if isinstance(v, (dict, list)):
            v_str = json.dumps(v, ensure_ascii=False)
        else:
            v_str = str(v)
        lines.append(f"IF {k} THEN {v_str}")

    out_txt_path.parent.mkdir(parents=True, exist_ok=True)
    out_txt_path.write_text("\n".join(lines), encoding="utf-8")


def if_then_to_json(txt_path: Path, out_json_path: Path) -> None:
    txt_path = Path(txt_path)
    out_json_path = Path(out_json_path)

    rules: Dict[str, Any] = {}
    with txt_path.open("r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            m = _IFTHEN_RE.match(line)
            if not m:
                raise ValueError(
                    f"Line {lineno} is not a valid IF ... THEN ... rule: {line!r}"
                )
            key, val_raw = m.group(1).strip(), m.group(2).strip()
            # Try to interpret the value as JSON (so numbers, objects, lists keep type)
            try:
                val = json.loads(val_raw)
            except Exception:
                val = val_raw
            if key in rules:
                # convert to list if multiple values for same key
                if isinstance(rules[key], list):
                    rules[key].append(val)
                else:
                    rules[key] = [rules[key], val]
            else:
                rules[key] = val

    out_json_path.parent.mkdir(parents=True, exist_ok=True)
    with out_json_path.open("w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Convert between JSON rules and IF ... THEN ... txt format"
    )
    p.add_argument(
        "basename", help="file basename without extension (reads/writes .json or .txt)"
    )
    p.add_argument(
        "format",
        choices=["txt", "json"],
        help='Desired output format. If "txt", read .json and write .txt; if "json", read .txt and write .json',
    )
    args = p.parse_args(argv)

    basename = args.basename
    dest_format = args.format
    src_format = "json" if dest_format == "txt" else "txt"

    src = Path(basename).with_suffix(f".{src_format}")
    dest = Path(basename).with_suffix(f".{dest_format}")

    if not src.exists():
        print(f"Source file not found: {src}", file=sys.stderr)
        sys.exit(2)

    try:
        if dest_format == "txt":
            json_to_if_then(src, dest)
        else:
            if_then_to_json(src, dest)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
