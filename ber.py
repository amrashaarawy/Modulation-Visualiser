"""
ber.py — performance view: bit error rate vs Eb/N0; theoretical formulas vs Monte Carlo simulation.

BER is derived from SER assuming Gray-coded constellations, so BER ~= SER / bits_per_symbol. 
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
from schemes import SCHEMES, modulate, add_noise


def Q(x):
    """Gaussian tail (one-sided)"""
    return 0.5 * erfc(x / np.sqrt(2))


def theoretical_ber(name, ebn0_db):
    """Closed-form BER for a scheme across an Eb/N0 (dB) array. Returns BER array."""
    ebn0_lin = 10 ** (ebn0_db / 10)

    if name == "BPSK":
        ber = Q(np.sqrt(2 * ebn0_lin))
    elif name == "QPSK":
        ber = Q(np.sqrt(2 * ebn0_lin))
    elif name == "16-QAM":
        M = 16
        ser = (4) * (1 - 1/np.sqrt(M)) * Q(np.sqrt(3*np.log2(M)/(M-1) * ebn0_lin))
        ber = ser / np.log2(M)

    return ber


def plot_ber(ebn0_db, n_bits=200000):
    """Overlay theoretical BER curves and Monte Carlo simulated points."""
    plt.figure(figsize=(8, 6))

    for name in SCHEMES:
        theory = theoretical_ber(name, ebn0_db)
        line, = plt.semilogy(ebn0_db, theory, label=f"{name} (theory)")
        color = line.get_color()                     # match sim dots to their line

        sim = [simulate_ber(name, snr, n_bits) for snr in ebn0_db]
        plt.plot(ebn0_db, sim, color=color, marker="o", markersize=6,
                linewidth=1, linestyle="-", label=f"{name} (sim)")

    plt.xlabel("Eb/N0 (dB)")
    plt.ylabel("Bit Error Rate")
    plt.title("BER vs Eb/N0 — theory vs Monte Carlo simulation")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=8)
    plt.ylim(1e-6, 1)
    plt.savefig("outputs/ber_overlay.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("wrote outputs/ber_overlay.png")

def demodulate(received, symbols_set):
    """Nearest-symbol decision"""
    diffs = received[:, None] - symbols_set[None, :]   # shape (n, m)
    distances = np.abs(diffs)                            
    decided_idx = np.argmin(distances, axis=1)            # shape (n,)
    return decided_idx

def simulate_ber(name, ebn0_db, n_bits):
    """Monte Carlo BER at one Eb/N0"""

    symbols = SCHEMES[name]["symbols"]
    bps = SCHEMES[name]["bits_per_symbol"]

    n_symbols = n_bits // bps
    sent, sent_idx = modulate(symbols, n_symbols)
    received = add_noise(sent, ebn0_db, bps)
    decided_idx = demodulate(received, symbols)

    symbol_errors = np.sum(sent_idx != decided_idx)
    ser = symbol_errors / n_symbols
    ber = ser / bps            # Gray SER->BER
    return ber



if __name__ == "__main__":
    ebn0_db = np.arange(0, 15)            # 0..14 dB sweep
    plot_ber(ebn0_db)