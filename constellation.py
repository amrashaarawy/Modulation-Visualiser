"""
constellation.py — geometry view: what each scheme looks like on the I/Q plane.
For each scheme: ideal symbols vs. real received cloud under noise, with decision boundaries drawn 
"""

import numpy as np
import matplotlib.pyplot as plt
from schemes import SCHEMES, modulate, add_noise

N_CLOUD = 2000


def decision_boundaries(name, ax):
    """Draw the decision-region borders for a scheme onto axis `ax`."""
    style = dict(color="red", linestyle="--", linewidth=1.0, alpha=0.7)

    if name == "BPSK":
        ax.axvline(0, label="decision boundary", **style)

    elif name == "QPSK":
        ax.axvline(0, label="decision boundary", **style)
        ax.axhline(0, **style)

    elif name == "16-QAM":
        symbols = SCHEMES[name]["symbols"]
        levels = np.unique(symbols.real)                 # 4 actual I-levels (already scaled)
        borders = (levels[:-1] + levels[1:]) / 2         # 3 midpoints between neighbours
        for i, b in enumerate(borders):
            lbl = "decision boundary" if i == 0 else None  
            ax.axvline(b, label=lbl, **style)
            ax.axhline(b, **style)

def plot_scheme(name, ebn0_db):
    """One figure per scheme: ideal points + decision boundaries + the real
    received clouds"""
    symbols = SCHEMES[name]["symbols"]
    bps = SCHEMES[name]["bits_per_symbol"]

    fig, ax = plt.subplots(figsize=(7, 7))          # single square axis

    # received noisy cloud 
    sent, idx = modulate(symbols, N_CLOUD)
    received = add_noise(sent, ebn0_db, bps)
    ax.scatter(received.real, received.imag, c=idx, cmap="tab20", s=10, alpha=0.6)

    # decision boundaries 
    decision_boundaries(name, ax)

    # ideal symbols on top of everything 
    ax.scatter(symbols.real, symbols.imag, color="black", marker="x",
           s=80, linewidths=2, zorder=5, label="transmitted symbol")

    ax.set_title(f"{name} — received cloud @ {ebn0_db} dB Eb/N0")
    ax.set_xlabel("In-phase (I)")
    ax.set_ylabel("Quadrature (Q)")
    ax.grid(True, alpha=0.3)
    ax.axis("equal")
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    fig.savefig(f"outputs/constellation_{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote outputs/constellation_{name}.png")


def plot_all(ebn0_db):
    """Produce the constellation figure for every scheme."""
    for name in SCHEMES:
        plot_scheme(name, ebn0_db)


if __name__ == "__main__":
    plot_all(ebn0_db=5)
    