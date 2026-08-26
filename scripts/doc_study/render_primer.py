#!/usr/bin/env python3
"""Render data/doc_study/<run>/global.json + rollup/*.json into a markdown
primer the same shape as plugin/GEOS_PRIMER_minimal.md.

Usage:
  python3 scripts/doc_study/render_primer.py \
      --run-dir data/doc_study/2026-05-18_full \
      --out plugin/GEOS_PRIMER_auto_2026-05-18.md
"""
import argparse
import json
import pathlib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    args = ap.parse_args()

    g = json.loads((args.run_dir / "global.json").read_text())

    lines: list[str] = []
    lines.append("# GEOS Primer (auto-generated)")
    lines.append("")
    lines.append(f"*Auto-generated from {args.run_dir} via doc-study pipeline "
                 "(DSv4-flash → studied artifact $\\hat D$).*")
    lines.append("")
    lines.append("**Elevator pitch.** " + g.get("elevator_pitch", "?"))
    lines.append("")
    lines.append("## Entrypoints")
    for e in g.get("entrypoints", []):
        lines.append(f"- {e}")
    lines.append("")
    lines.append("## Top workflows")
    for w in g.get("top_workflows", []):
        lines.append(f"- {w}")
    lines.append("")
    lines.append("## Primary object taxonomy")
    tax = g.get("primary_object_taxonomy", {}) or {}
    for cat, items in tax.items():
        lines.append(f"### {cat}")
        lines.append(", ".join(f"`{x}`" for x in items))
        lines.append("")
    lines.append("## Top pitfalls")
    for p in g.get("top_pitfalls", []):
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## Navigation index")
    for k, v in (g.get("navigation_index", {}) or {}).items():
        lines.append(f"- **{k}** → `{v}`")
    lines.append("")
    lines.append("## Coverage note")
    lines.append(g.get("coverage_note", "?"))
    lines.append("")

    # Append per-subtree section navigation hints
    lines.append("---")
    lines.append("")
    lines.append("## Subtree navigation hints (from per-subtree rollups)")
    lines.append("")
    rollup_dir = args.run_dir / "rollup"
    for f in sorted(rollup_dir.glob("*.json")):
        try:
            r = json.loads(f.read_text())
        except Exception:
            continue
        subtree = r.get("subtree") or f.stem
        purpose = r.get("purpose", "")
        nav = r.get("navigation_hints", "")
        lines.append(f"### `{subtree}`")
        if purpose:
            lines.append(f"**Purpose.** {purpose}")
        if nav:
            lines.append(f"**Find here.** {nav}")
        prim = r.get("primary_xml_elements") or []
        if prim:
            lines.append("**Key XML elements:** " + ", ".join(f"`{x}`" for x in prim[:10]))
        lines.append("")

    args.out.write_text("\n".join(lines))
    print(f"wrote {args.out}  ({len(lines)} lines)")


if __name__ == "__main__":
    main()
