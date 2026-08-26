"""Analyze Liam's full-run (post-cutoff catch-up) browser history.

The original 1h session was 04/24/26 (analyzed in
scripts/analyze_human_browser_history.py). Liam returned and finished the
assignment on 05/06/26. We characterize the catch-up session and combine it
with the original session for the full-run total.
"""

import csv
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("/home/matt/sci/repo3")
HUMAN_DIR = ROOT / "data/human_baseline"
ORIG = HUMAN_DIR / "liam_browser_data.csv"
FIN = HUMAN_DIR / "liam_fin_folder/liam_fin_browser_history.csv"


def domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return "?"


def categorize(url: str, title: str) -> str:
    u = url.lower()
    t = (title or "").lower()
    if "geosx" in u or "geos.readthedocs" in u:
        return "GEOS docs (Sphinx/doxygen)"
    if "github.com/geos" in u:
        return "GEOS source (github)"
    if "stackoverflow.com" in u or "stackexchange.com" in u:
        return "Stack Overflow / SE"
    if "google.com/search" in u or "bing.com/search" in u or "duckduckgo.com" in u:
        return "search engine"
    if "wikipedia.org" in u:
        return "Wikipedia"
    if "youtube.com" in u or "youtu.be" in u:
        return "YouTube"
    if "slack" in u:
        return "Slack"
    if "chatgpt" in u or "openai.com/chat" in u or "claude.ai" in u or "anthropic" in u or "perplexity" in u:
        return "LLM chatbot (DISALLOWED)"
    if "doi.org" in u or "arxiv.org" in u or "researchgate" in u or "sciencedirect" in u or "springer" in u:
        return "scientific paper"
    if u.startswith("file://"):
        return "local file"
    if "rcic.uci.edu" in u:
        return "cluster docs (env/run)"
    return "other"


def load_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def filter_session(rows: list[dict], date: str) -> list[dict]:
    return [r for r in rows if r.get("date", "") == date]


def report(rows: list[dict], label: str) -> dict:
    cats = Counter(categorize(r.get("url", ""), r.get("title", "")) for r in rows)
    domains = Counter(domain_of(r.get("url", "")) for r in rows)
    print(f"\n=== {label} ===  ({len(rows)} visits)")
    print(f"unique domains: {len(domains)}")
    print("\nCategory breakdown:")
    for c, n in sorted(cats.items(), key=lambda kv: -kv[1]):
        print(f"  {c:35s}  {n}")
    print("\nTop domains:")
    for d, n in domains.most_common(8):
        print(f"  {d:50s}  {n}")
    return {"n": len(rows), "categories": dict(cats), "domains": dict(domains)}


def find_disallowed(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        cat = categorize(r.get("url", ""), r.get("title", ""))
        if cat.startswith("LLM"):
            out.append(r)
    return out


def page_titles(rows: list[dict], filter_cat: str | None = None) -> list[str]:
    titles = []
    for r in rows:
        cat = categorize(r.get("url", ""), r.get("title", ""))
        if filter_cat and cat != filter_cat:
            continue
        titles.append(r.get("title", ""))
    return titles


def top_pages(rows: list[dict], top_n: int = 12) -> list[tuple[str, int]]:
    counter = Counter()
    for r in rows:
        cat = categorize(r.get("url", ""), r.get("title", ""))
        if cat.startswith("GEOS"):
            counter[r.get("title", "")] += 1
    return counter.most_common(top_n)


def main() -> None:
    orig = filter_session(load_csv(ORIG), "04/24/26")
    fin = filter_session(load_csv(FIN), "05/06/26")
    combined = orig + fin

    report(orig, "Liam ORIGINAL 1h session (04/24/26)")
    report(fin, "Liam CATCH-UP session (05/06/26)")
    report(combined, "Liam FULL RUN (combined)")

    print("\n=== Disallowed visits (LLM chatbots) ===")
    for label, rs in [("orig", orig), ("fin", fin)]:
        d = find_disallowed(rs)
        if d:
            print(f"  {label}: {len(d)} visit(s)")
            for r in d:
                print(f"    {r.get('time', '?')}  {r.get('title', '')}")
        else:
            print(f"  {label}: 0")

    print("\n=== Top GEOS pages in catch-up session ===")
    for title, n in top_pages(fin):
        print(f"  ({n}x) {title[:120]}")


if __name__ == "__main__":
    main()
