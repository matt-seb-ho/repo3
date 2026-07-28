"""Render the SPE10-bottom-layers initial configuration & heterogeneity map.

Reads the GEOS voxel tables that the TutorialDeadOilBottomLayersSPE10
experiment uses and overlays the 5 well boxes from the benchmark XML.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle

REPO = Path(__file__).resolve().parents[1]
DATA_DIR = REPO / "data/GEOS/inputFiles/compositionalMultiphaseFlow/benchmarks/SPE10"
OUT_DIR = REPO / "data/eval"
OUT_PATH = OUT_DIR / "spe10_initial_config.png"

NX, NY, NZ = 60, 220, 2
EXTENT = [0.0, 365.76, 0.0, 670.56]
MD_TO_M2 = 9.869233e-16

WELLS = [
    ("source", (182.85, 335.25), (189.00, 338.35), "#39ff14", "Center Water Source (Water Injection)"),
    ("sink1",  (-0.01,   -0.01), (6.126,   3.078), "#ff2d2d", "Corner Sinks (Fluid Production)"),
    ("sink2",  (-0.01,  667.482),(6.126,  670.60), "#ff2d2d", None),
    ("sink3",  (359.634, -0.01), (365.8,   3.048), "#ff2d2d", None),
    ("sink4",  (359.634, 667.482),(365.8, 670.60), "#ff2d2d", None),
]

MARKER_HALF_W = 18.0
MARKER_HALF_H = 18.0


def load_voxel(name: str) -> np.ndarray:
    """Load a GEOS voxel file and reshape to (NX, NY, NZ) with x fastest."""
    flat = np.loadtxt(DATA_DIR / name)
    return flat.reshape((NZ, NY, NX)).transpose(2, 1, 0)


def main() -> None:
    permx = load_voxel("permx.geos") * MD_TO_M2
    layer = permx[:, :, 0]

    fig, ax = plt.subplots(figsize=(5.2, 8.0), dpi=160)
    fig.patch.set_facecolor("white")

    im = ax.imshow(
        layer.T,
        origin="lower",
        extent=EXTENT,
        norm=LogNorm(vmin=max(layer.min(), 1e-18), vmax=layer.max()),
        cmap="turbo",
        aspect="equal",
        interpolation="nearest",
    )

    for _, (x0, y0), (x1, y1), color, label in WELLS:
        cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        cx = float(np.clip(cx, EXTENT[0] + MARKER_HALF_W, EXTENT[1] - MARKER_HALF_W))
        cy = float(np.clip(cy, EXTENT[2] + MARKER_HALF_H, EXTENT[3] - MARKER_HALF_H))
        ax.add_patch(
            Rectangle(
                (cx - MARKER_HALF_W, cy - MARKER_HALF_H),
                2 * MARKER_HALF_W, 2 * MARKER_HALF_H,
                facecolor=color, edgecolor="black", linewidth=1.2,
                label=label,
            )
        )

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)  —  long axis of the slab")
    ax.set_xlim(EXTENT[0], EXTENT[1])
    ax.set_ylim(EXTENT[2], EXTENT[3])

    cbar = fig.colorbar(im, ax=ax, shrink=0.55, pad=0.02)
    cbar.set_label("Permeability  k  (m²,  log scale)")

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.14),
              ncol=2, frameon=False, fontsize=8)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, bbox_inches="tight", dpi=200)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
