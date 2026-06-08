#!/usr/bin/env bash
#
# make_arxiv_upload.sh — stage the MINIMAL set of files arXiv needs and zip them.
#
# It reads the main .tex, follows every active (non-commented) \includegraphics,
# \promptinput / \VerbatimInput, and \input reference, plus any local .sty used by
# \usepackage, and copies ONLY those files (preserving relative paths) into a clean
# staging folder. It includes the precompiled .bbl so arXiv does not need the .bib.
# It then test-compiles the staged folder to prove the set is complete, strips the
# build artifacts, and produces arxiv_upload.zip.
#
# Usage:
#   ./make_arxiv_upload.sh [MAIN_TEX]
#   MAIN_TEX defaults to arxiv_v1.tex
#
set -euo pipefail

MAIN="${1:-arxiv_v1.tex}"
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

STAGE="arxiv_upload"
ZIP="arxiv_upload.zip"
BASE="${MAIN%.tex}"

[[ -f "$MAIN" ]] || { echo "ERROR: main tex '$MAIN' not found in $HERE" >&2; exit 1; }

echo ">> main file: $MAIN"
rm -rf "$STAGE" "$ZIP"
mkdir -p "$STAGE"

# --- helper: strip TeX comments (everything after an unescaped %) ----------------
strip_comments() { sed -E 's/([^\\])%.*/\1/; s/^%.*//' "$1"; }

# --- collect referenced files ----------------------------------------------------
# Extract the {path} argument of a command, ignoring optional [..] and macro params.
extract_args() { # $1 = command name (no backslash)
  strip_comments "$MAIN" \
    | grep -oE "\\\\$1(\\[[^]]*\\])?\\{[^}]*\\}" \
    | sed -E "s/\\\\$1(\\[[^]]*\\])?\\{([^}]*)\\}/\\2/" \
    | grep -v '#'        # drop macro-definition placeholders like {#2}
}

declare -a FILES=()

# 1) graphics (may be given without extension)
while IFS= read -r p; do
  [[ -z "$p" ]] && continue
  if [[ -f "$p" ]]; then
    FILES+=("$p")
  else
    # resolve missing extension (png/pdf/jpg/jpeg/eps)
    match="$(ls "$p".{png,pdf,jpg,jpeg,eps} 2>/dev/null | head -n1 || true)"
    [[ -n "$match" ]] && FILES+=("$match") || { echo "ERROR: graphics not found: $p" >&2; exit 1; }
  fi
done < <(extract_args includegraphics)

# 2) verbatim inputs (\promptinput wraps \VerbatimInput; capture both, literal paths)
while IFS= read -r p; do
  [[ -z "$p" ]] && continue
  [[ -f "$p" ]] && FILES+=("$p") || { echo "ERROR: verbatim input not found: $p" >&2; exit 1; }
done < <( { extract_args promptinput; extract_args VerbatimInput; } )

# 3) \input{...} (append .tex if no extension)
while IFS= read -r p; do
  [[ -z "$p" ]] && continue
  [[ "$p" == *.* ]] || p="$p.tex"
  [[ -f "$p" ]] && FILES+=("$p") || { echo "ERROR: \\input target not found: $p" >&2; exit 1; }
done < <(extract_args input)

# 4) local style files pulled in by \usepackage (e.g. neurips_2026.sty)
while IFS= read -r pkglist; do
  IFS=',' read -ra pkgs <<< "$pkglist"
  for pkg in "${pkgs[@]}"; do
    pkg="$(echo "$pkg" | tr -d ' ')"
    [[ -f "$pkg.sty" ]] && FILES+=("$pkg.sty")
  done
done < <(strip_comments "$MAIN" | grep -oE '\\usepackage(\[[^]]*\])?\{[^}]*\}' \
         | sed -E 's/\\usepackage(\[[^]]*\])?\{([^}]*)\}/\2/')

# 5) the main tex itself, and the precompiled bibliography (.bbl, so arXiv skips bibtex)
FILES+=("$MAIN")
if [[ -f "$BASE.bbl" ]]; then
  FILES+=("$BASE.bbl")
else
  echo "WARNING: $BASE.bbl not found — run: pdflatex $MAIN && bibtex $BASE && pdflatex $MAIN" >&2
fi

# --- copy (dedup, preserve relative dirs) ----------------------------------------
echo ">> staging files:"
printf '%s\n' "${FILES[@]}" | sort -u | while IFS= read -r f; do
  mkdir -p "$STAGE/$(dirname "$f")"
  cp "$f" "$STAGE/$f"
  printf '   %s\n' "$f"
done

# --- verify the minimal set actually compiles ------------------------------------
if command -v pdflatex >/dev/null 2>&1; then
  echo ">> test-compiling staged folder ..."
  (
    cd "$STAGE"
    pdflatex -interaction=nonstopmode -halt-on-error "$MAIN" >/dev/null 2>&1
    pdflatex -interaction=nonstopmode -halt-on-error "$MAIN" >/dev/null 2>&1
    undef="$(grep -c 'undefined' "$BASE.log" 2>/dev/null || true)"; undef="${undef:-0}"
    pages="$(pdfinfo "$BASE.pdf" 2>/dev/null | awk '/Pages/{print $2}')"
    echo "   compiled OK: ${pages:-?} pages, $undef undefined-reference warnings"
    [[ "$undef" -gt 0 ]] && echo "   WARNING: undefined references remain — inspect $STAGE/$BASE.log" >&2 || true
  )
  # strip build artifacts so the upload contains only source
  ( cd "$STAGE" && rm -f "$BASE".{aux,log,out,blg,pdf} )
else
  echo ">> pdflatex not found; skipping verification compile."
fi

# --- zip -------------------------------------------------------------------------
( cd "$STAGE" && zip -qr "../$ZIP" . )
echo ">> wrote $ZIP"
echo "   contents:"
unzip -l "$ZIP" | sed 's/^/   /'
echo
echo "Upload $ZIP to arXiv (or upload the contents of the '$STAGE/' folder)."
