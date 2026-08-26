"""All numbers transcribed verbatim from writing/arxiv/neurips_2026.tex.
Each block cites the source table label so it can be re-checked against the paper.
"""

# ── Table 1 (tab:main-results): cell-level TreeSim, held-out-eval split ───────
# cells that actually have held-out-eval numbers (mean, std)
HELDOUT = [
    # cell,        mean,   std
    ("Vanilla",    0.720, 0.081),
    ("X+M",        0.768, 0.005),
    ("S+X",        0.781, 0.002),
    ("S+X+M",      0.783, 0.022),
    ("SE-prose",   0.775, 0.024),
    ("SE",         0.789, 0.012),
]
# val split for the same cells (mean, std) — for the ceiling comparison
VAL = {
    "Vanilla":  (0.910, 0.024),
    "X+M":      (0.921, 0.007),
    "S+X":      (0.917, 0.004),
    "S+X+M":    (0.911, 0.018),
    "SE-prose": (0.897, 0.032),
    "SE":       (0.919, 0.020),
}

# ── Per-task held-out-eval (tab:per-task-icl10): Vanilla & SE columns ─────────
# (task, vanilla, se); sorted ascending by Vanilla as in the paper
PER_TASK = [
    ("TutorialHydraulicFractureWithAdvancedXML",    0.013, 0.013),
    ("AdvancedExampleThermoPoroElasticWellbore",    0.355, 0.761),  # rescue
    ("ExampleProppantTest",                         0.541, 0.825),  # rescue
    ("ExampleIsothermalHystInjection",              0.755, 0.717),
    ("AdvancedExampleCasedThermoElasticWellbore",   0.847, 0.886),
    ("ExamplesingleFracCompression",                0.891, 0.928),
    ("ExampleVerticalPoroElastoPlasticWellbore",    0.909, 0.944),
    ("ExampleMCCWellbore",                          0.935, 0.941),
    ("AdvancedExamplePureThermalDiffusionWellbore", 0.963, 0.880),
    ("AdvancedExampleViscoExtendedDruckerPrager",   0.986, 0.996),
]
RESCUE_TASKS = {"AdvancedExampleThermoPoroElasticWellbore", "ExampleProppantTest"}

# ── Table 2 (tab:human-baseline): deck-level quality vs wall-clock ───────────
# label, deck_level_score, deck_is_lower_bound(>=), wall_minutes, file_level, kind
HUMAN = [
    ("Expert 1 (1h cutoff)",    0.540, False, 48.2,  0.812, "human"),
    ("Expert 2 (1h cutoff)",    0.527, False, 46.7,  0.781, "human"),
    ("Expert 1 (no cap)",       0.931, False, 180.0, 0.689, "human"),
    ("Vanilla CC",              0.751, False, 7.0,   0.889, "agent_base"),
    ("SIGA X+M",                0.900, True,  5.0,   0.900, "agent_siga"),  # >= 0.90
]

# ── Table 3 (tab:cross-cutting-full): cross-model & cross-harness ────────────
# harness, backbone, n, vanilla, xm, se(None if absent), vanilla_fail, xm_fail, se_fail
CROSS = [
    ("CC", "deepseek-v4-flash", 3, 0.910, 0.921, 0.919, 0, 0, 0),
    ("CC", "minimax-m2.7",      1, 0.821, 0.867, 0.861, 1, 0, 0),
    ("CC", "gemini-3-flash-preview", 1, 0.768, 0.797, 0.757, 0, 0, 1),
    ("OH", "deepseek-v4-flash", 3, 0.856, 0.881, None,  0, 0, None),
]

# ── Table 4 (tab:openfoam-summary): mean score, coverage ────────────────────
# cell, mean, delta_vs_vanilla, full_coverage_k(of 5), has_S, kind
OPENFOAM_SUMMARY = [
    ("Vanilla",          0.466,  None,   3, False, "baseline"),
    ("R+M",              0.736,  0.270,  5, False, "cell"),
    ("S+M",              0.787,  0.321,  5, True,  "cell"),
    ("R+S",              0.871,  0.405,  5, True,  "cell"),   # best
    ("X+M",              0.712,  0.246,  5, False, "cell"),
    ("R+X",              0.145, -0.321,  1, False, "cell"),   # catastrophic
    ("S+X",              0.849,  0.383,  5, True,  "cell"),
    ("R+S+X+M",          0.862,  0.396,  5, True,  "cell"),
    ("S+X+M",            0.822,  0.356,  5, True,  "cell"),
    ("Foam-Agent (lint)",0.569,  0.103,  3, False, "baseline"),
]
# OpenFOAM factor-style main effects (tab text)
OPENFOAM_FACTORS = {"R": -0.050, "S": 0.328, "X": -0.073, "M": 0.192}

# ── Table 4b (tab:openfoam-per-task): cells × 5 tasks ───────────────────────
OPENFOAM_TASKS = ["boundaryWall\nFunctionsProfile", "Grossetete", "helmholtz\nResonance",
                  "externalCoupled\nCavity", "damBreak\nWithObstacle"]
OPENFOAM_PER_TASK = [
    # cell,            5 task scores,                              has_S
    ("Vanilla",          [0.751, 0.817, 0.000, 0.762, 0.000], False),
    ("R+M",              [0.650, 0.817, 0.681, 1.000, 0.532], False),
    ("S+M",              [0.860, 0.966, 0.788, 0.595, 0.723], True),
    ("R+S",              [0.907, 0.968, 0.858, 0.900, 0.723], True),
    ("X+M",              [0.719, 0.820, 0.727, 0.762, 0.531], False),
    ("R+X",              [0.724, 0.000, 0.000, 0.000, 0.000], False),
    ("S+X",              [0.965, 0.870, 0.787, 0.899, 0.723], True),
    ("R+S+X+M",          [0.964, 0.967, 0.760, 0.899, 0.722], True),
    ("S+X+M",            [0.807, 0.788, 0.850, 0.943, 0.722], True),
    ("Foam-Agent (lint)",[0.657, 0.165, 0.649, 0.636, 0.736], False),
]

# ── Table bottleneck (tab:bottleneck): failure categories, val split ────────
# category, Vanilla, X+M, SE   (val panel, n=51)
FAILURE_CATS = [
    ("bad_attribute_value",   12, 11,  9),
    ("structural_mismatch",    6,  7, None),  # SE '-' in paper -> not recorded
    ("extra_block",            9, 11, 10),
    ("partial_implementation", 7,  6,  9),
    ("missing_block",          6,  3, None),  # SE '-' in paper
    ("hallucinated_extras",    4,  7, None),  # SE '-' in paper
]
