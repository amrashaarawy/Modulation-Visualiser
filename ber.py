"""
ber.py — performance view: bit error rate vs Eb/N0; theoretical formulas vs Monte Carlo simulation.

BER is derived from SER assuming Gray-coded constellations, so BER ~= SER / bits_per_symbol. 
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
from schemes import SCHEMES


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
        ser = (4/np.sqrt(M)) * (1 - 1/np.sqrt(M)) * Q(np.sqrt(3*np.log2(M)/(M-1) * ebn0_lin))
        ber = ser / np.log2(M)

    return ber


def plot_ber(ebn0_db):
    """Overlay theoretical BER curves for all schemes on one semilogy plot"""
    plt.figure(figsize=(8, 6))
    for name in SCHEMES:
        ber = theoretical_ber(name, ebn0_db)
        plt.semilogy(ebn0_db, ber, label=f"{name} (theory)")

    plt.xlabel("Eb/N0 (dB)")
    plt.ylabel("Bit Error Rate")
    plt.title("Theoretical BER vs Eb/N0")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.ylim(1e-6, 1)                    
    plt.savefig("outputs/ber_theoretical.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("wrote outputs/ber_theoretical.png")


# --- tomorrow: simulation half ---
def demodulate(received, symbols_set):
    """Nearest-symbol decision. Returns decided indices. (built tomorrow)"""
    raise NotImplementedError


def simulate_ber(name, ebn0_db, n):
    """Monte Carlo BER at one Eb/N0. (built tomorrow)"""
    raise NotImplementedError


if __name__ == "__main__":
    ebn0_db = np.arange(0, 15)            # 0..14 dB sweep
    plot_ber(ebn0_db)