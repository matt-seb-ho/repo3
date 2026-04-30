#!/usr/bin/env bash
# Launch one (condition, seed) of the dsv4_ablation_2026-04-29 matrix.
#
# Usage:
#   ./scripts/launch_dsv4_ablation.sh <condition> <seed>
#
#   <condition> ∈ {c0, c2, c3, c4}
#   <seed>      ∈ {1, 2, 3}
#
# Writes results to /data/shared/geophysics_agent_data/data/eval/dsv4_ablation_2026-04-29/
# Logs to /data/shared/geophysics_agent_data/data/eval/dsv4_ablation_2026-04-29/_logs/
set -euo pipefail

cd /home/matt/sci/repo3

# Load DSv4 direct API
source .env
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"

COND="${1:?cond required}"
SEED="${2:?seed required}"

case "$COND" in
  c0) AGENT="abl_c0_true_vanilla";        PRIMER="plugin/GEOS_PRIMER_absolute_min.md" ;;
  c2) AGENT="abl_c2_min_sr_no_rag";       PRIMER="plugin/GEOS_PRIMER_minimal_vanilla.md" ;;
  c3) AGENT="abl_c3_min_rag_no_sr";       PRIMER="plugin/GEOS_PRIMER_minimal.md" ;;
  c4) AGENT="abl_c4_min_rag_sr";          PRIMER="plugin/GEOS_PRIMER_minimal.md" ;;
  c5) AGENT="abl_c5_dsv4_mem";            PRIMER="plugin/GEOS_PRIMER_minimal_vanilla.md" ;;
  *) echo "unknown condition: $COND" >&2; exit 2 ;;
esac

RUN_NAME="${COND}_dsv4_s${SEED}"
RESULTS_ROOT="/data/shared/geophysics_agent_data/data/eval/dsv4_ablation_2026-04-29"
LOG_DIR="$RESULTS_ROOT/_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${RUN_NAME}.log"

echo "=== Launching $RUN_NAME ($AGENT, primer=$PRIMER) at $(date -u +%FT%TZ) ===" | tee "$LOG_FILE"

python3 scripts/run_experiment.py \
  --run "$RUN_NAME" \
  --agents "$AGENT" \
  --workers 4 \
  --timeout 1200 \
  --strip-baked-primer \
  --geos-primer-path "$PRIMER" \
  --tmp-geos-parent /data/matt/geos_eval_tmp \
  --experiments-dir /data/shared/geophysics_agent_data/data/eval/experiments_test36_template \
  --ground-truth-dir /data/shared/geophysics_agent_data/data/eval/experiments_gt \
  --include AdvancedExampleCasedContactThermoElasticWellbore AdvancedExampleDeviatedElasticWellbore AdvancedExampleDruckerPrager AdvancedExampleExtendedDruckerPrager AdvancedExampleModifiedCamClay AdvancedExampleViscoDruckerPrager buckleyLeverettProblem ExampleDPWellbore ExampleEDPWellbore ExampleIsothermalLeakyWell ExampleMandel ExampleThermalLeakyWell ExampleThermoporoelasticConsolidation kgdExperimentValidation pknViscosityDominated TutorialPoroelasticity TutorialSneddon \
  --results-root-dir "$RESULTS_ROOT" \
  --claude-model deepseek-v4-flash \
  >> "$LOG_FILE" 2>&1

echo "=== Done $RUN_NAME at $(date -u +%FT%TZ) ===" >> "$LOG_FILE"
