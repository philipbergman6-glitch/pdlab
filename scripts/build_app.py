#!/usr/bin/env python3
"""Inject the canonical results payload into app/template.html -> app/index.html.

Hard-fails if the payload is missing, is not valid JSON, or if the template does
not contain the literal placeholder ``/*__PAYLOAD__*/null``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLACEHOLDER = "/*__PAYLOAD__*/null"
ROOT = Path(__file__).resolve().parent.parent


def build(payload_path: Path, template_path: Path, out_path: Path) -> Path:
    if not payload_path.is_file():
        raise SystemExit(f"build_app: payload not found: {payload_path}")
    if not template_path.is_file():
        raise SystemExit(f"build_app: template not found: {template_path}")

    raw = payload_path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"build_app: {payload_path} is not valid JSON: {exc}") from exc

    template = template_path.read_text(encoding="utf-8")
    if template.count(PLACEHOLDER) != 1:
        raise SystemExit(
            f"build_app: expected exactly one {PLACEHOLDER!r} in {template_path}, "
            f"found {template.count(PLACEHOLDER)}"
        )

    # separators/ensure_ascii keep the blob compact and free of raw non-ASCII;
    # "</" is escaped so a stray token can never close the <script> element.
    blob = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")
    html = template.replace(PLACEHOLDER, blob)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build the single-file pdlab app.")
    ap.add_argument(
        "--payload",
        default=str(ROOT / "results" / "app_payload.json"),
        help="path to app_payload.json (default: results/app_payload.json)",
    )
    ap.add_argument("--template", default=str(ROOT / "app" / "template.html"))
    ap.add_argument("--out", default=str(ROOT / "app" / "index.html"))
    args = ap.parse_args(argv)

    out = build(Path(args.payload), Path(args.template), Path(args.out))
    size_kb = out.stat().st_size / 1024
    print(f"build_app: wrote {out} ({size_kb:.1f} kB) from {args.payload}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
