"""
schemes.py — source of truth for the modulation schemes.
each scheme's symbols are normalized to unit average energy 
"""

import numpy as np


def normalize(symbols):
    """Scales a symbol set to unit average energy"""

    avg_energy = np.mean(np.abs(symbols) ** 2)
    return symbols / np.sqrt(avg_energy)


# BPSK - raw avg energy already 1
bpsk = normalize(np.array([-1, 1], dtype=complex))

# QPSK
qpsk = normalize(np.array([1+1j, -1+1j, -1-1j, 1-1j]))


# 16-QAM
levels = np.array([-3, -1, 1, 3])
qam16_raw = np.array([  i + 1j*q  for i in levels  for q in levels ])
qam16 = normalize(qam16_raw)


SCHEMES = {
    "BPSK":   {"symbols": bpsk,   "bits_per_symbol": 1},
    "QPSK":   {"symbols": qpsk,   "bits_per_symbol": 2},
    "16-QAM": {"symbols": qam16,  "bits_per_symbol": 4},
    # ber_func to be added to each scheme
}

#symbol generation
def modulate(symbols_set, n):
    """Pick n random symbols from a scheme's constellation - returns symbols and indices"""

    indices = np.random.randint(0, len(symbols_set), size=n)
    return symbols_set[indices], indices

def add_noise(symbols, ebn0_db, bits_per_symbol):
    """Add complex Gaussian (AWGN) noise at the given Eb/N0."""

    ebn0_linear = 10 ** (ebn0_db / 10)              # dB -> linear ratio
    n0 = 1 / (bits_per_symbol * ebn0_linear)        # Es=1 -> Eb=1/bps -> N0=Eb/ratio
    noise_std = np.sqrt(n0 / 2)                      # /2 splits power across I and Q
    noise = noise_std * (np.random.randn(len(symbols))
                         + 1j * np.random.randn(len(symbols)))
    return symbols + noise



# self check
if __name__ == "__main__":
    for name, s in SCHEMES.items():
        avg_e = np.mean(np.abs(s["symbols"]) ** 2)
        print(f"{name:7s} | {len(s['symbols']):2d} symbols | avg energy = {avg_e:.4f}")

    # smoke-test the channel primitives
    sent, idx = modulate(SCHEMES["QPSK"]["symbols"], 5)
    rx = add_noise(sent, ebn0_db=10, bits_per_symbol=2)
    print(f"\nmodulate -> {len(sent)} symbols, indices {idx}")
    print(f"add_noise -> {len(rx)} noisy points (first: {rx[0]:.3f})")