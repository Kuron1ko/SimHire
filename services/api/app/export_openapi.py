from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.main import create_app


def export_openapi(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    schema = create_app().openapi()
    output.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the SimHire OpenAPI document.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("openapi.json"),
        help="Destination path for the generated OpenAPI JSON.",
    )
    args = parser.parse_args()
    export_openapi(args.output)


if __name__ == "__main__":
    main()
