# Modulation Visualiser + AWGN BER Simulator

Constellation diagrams and bit-error-rate analysis for BPSK, QPSK, and 16-QAM
over an AWGN channel. Theoretical BER curves are validated against an
independent Monte Carlo simulation of the full transmit, noise, demodulation chain.

## What it does

- **Constellation diagrams** — ideal symbol positions, decision boundaries, and
  the real received point cloud (from an actual simulated transmission, not
  an illustrative noise model), overlaid at multiple Eb/N0 levels so symbol
  errors are visible directly on the plot.
- **BER curves** — closed-form theoretical BER for each scheme, overlaid with
  Monte Carlo simulated BER, on a log-scale axis.

## Architecture

Three modules, split by concern:

| File | Role |
|---|---|
| `schemes.py` | Single source of truth: normalized symbol sets, `SCHEMES` dict, and the shared channel primitives (`modulate`, `add_noise`) used by both other modules. |
| `constellation.py` | Geometry view — what each scheme looks like on the I/Q plane under noise. |
| `ber.py` | Performance view — theoretical vs. simulated bit error rate across Eb/N0. |

Theory and simulation live in one file (`ber.py`) rather than two, because
they're one concern — computing and validating the same quantity — not two;
splitting them would separate code that has to be read together.

## Key design decisions

- **Unit average energy normalization.** Every constellation is scaled so
  `mean(|symbol|²) = 1`. Without this, denser constellations (e.g. 16-QAM)
  would carry more raw power and look artificially more/less robust — BER
  comparisons across schemes are only fair at equal power.
- **Dict-based schemes, not classes.** Each scheme is pure data (symbols,
  bits/symbol) plus shared, not per-scheme, behaviour. No behavioural
  variation exists that would justify OOP here.
- **Received clouds come from the real simulation**, not a separate
  illustrative noise draw — `constellation.py` and `ber.py` both call the same
  `modulate`/`add_noise` primitives from `schemes.py`, so the picture and the
  BER number are two views of the same experiment, not two different models.
- **Decision boundaries are derived from the symbols**, not hard-coded — for
  16-QAM, boundaries are the midpoints between `np.unique`'d symbol levels, so
  they stay correct regardless of the normalization factor.
- **BER is approximated from SER via Gray coding**: `BER ≈ SER / log₂M`,
  assuming adjacent symbols differ by one bit and errors land in adjacent
  decision regions. Standard, valid at moderate-to-high SNR (see limitations).
- **The demapper is a vectorized nearest-neighbour decision** — pairwise
  broadcast distance (`received[:,None] - symbols[None,:]`) + `argmin`.

## Running it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 schemes.py         # normalized energies + primitives
python3 constellation.py   # writes constellation PNGs to outputs/
python3 ber.py             # writes the BER overlay PNG to outputs/
```

## Outputs
 
`outputs/` contains constellation diagrams for each scheme at two Eb/N0
levels (5 dB, 10 dB), showing the density/robustness tradeoff — 16-QAM's
denser packing shows visibly more boundary-crossing than BPSK/QPSK at the
same noise level — plus the theory-vs-simulation BER overlay.


## Known limitations

- **The Gray-coding approximation weakens at low SNR.** Because 16-QAM's
  per-bit dilution factor (÷4) is strong, its *bit* error rate briefly dips
  *below* BPSK/QPSK's near 0 dB, even though its *symbol* error rate is
  always higher. This is a real effect of the model, in a region with no
  practical relevance — and it's exactly where the approximation is weakest,
  since it assumes errors only reach adjacent symbols.
- **Monte Carlo simulation has a hard sampling floor.** With a fixed sample
  size (200k bits), reliably measuring BER below ~1e-5 would need ~10⁷–10⁸
  bits. At high Eb/N0, some runs measure zero errors — `log(0)` is undefined,
  so those points vanish or plunge to the plot's floor. Not a bug: this is
  why the theoretical curve is shown alongside the simulation rather than
  instead of it.
- **AWGN only** — no channel coding, pulse shaping, synchronization, or
  fading. Deliberately out of scope.

## Validation

- **Theoretical and simulated BER curves agree closely** across the sweep —
  the actual correctness proof for the simulator, since an independent
  nearest-neighbour demapper reproduces the closed-form theory.
- **BPSK and QPSK curves coincide**, both analytically and in simulation —
  confirming QPSK's two independent I/Q bit streams achieve double the
  spectral efficiency at no BER cost.
- **The overlay caught a real bug during development**: an incorrect 16-QAM
  theoretical coefficient was found because simulated points consistently
  disagreed with theory by a factor of √M, before being corrected.

CI (GitHub Actions) runs all three modules end-to-end on every push, on a
clean install from `requirements.txt`.