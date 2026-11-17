# Chipalooza Challenge #4: programmable-gain inverter amplifier (Sky130)

Self-biased CMOS inverter amplifier with a switched input-resistor bank (8 gain codes),
a switched on-chip coupling-capacitor bank (off / 10 / 30 / 50 pF, external capacitor on CEXT),
a switched feedback-capacitor bank (0 / 1 / 4 / 16 pF) and an enable. 3.3 V analog supply.
The proposal is in `docs/`. Status: proposal stage; all v2 results are pre-layout schematic simulation.

## Layout of this repository

| Path | Contents |
|---|---|
| `v1/` | First-generation design (4 gain steps), as submitted to Tiny Tapeout SKY 25a: xschem schematics, Magic layout, extracted netlist (`mag/mixedsignal_rcx.spice`), GDS, LEF, docs |
| `v1/sim/` | v1 simulation scripts: schematic with the real transmission-gate mux (`v1val2.py`), post-layout extracted netlist (`v1rcx.py`, `v1_overlay.py`) |
| `v1/bench/` | `digitize_video_frames.py`: reads the Bode curves from frames of a bench screen recording (the video itself is not in the repo) |
| `v2/sim/` | v2 simulation scripts and design data (`rin_design.json`, input-resistor values) |
| `results/` | Summary plots (`results/plots/`) and small JSON/text summaries from the gap-closing runs (no raw data dumps) |
| `docs/` | Proposal document |

The v1 file and module names (`tt_um_..._mixedsignal`) are those of the Tiny Tapeout submission and are left
unchanged so that the GDS, LEF, Magic and extracted views stay consistent.

## v1 mux codes

Code = `ui_in[1:0]`. From the schematic: 00 = no parallel resistor (300 kohm feedback), 01 = 30 kohm path
(about 27 kohm), 10 = 3 kohm path (about 3 kohm), 11 = 100 kohm path (about 75 kohm).
Measured by an independent tester at 100 kHz, 20 mVpp in: 637, 222, 151, 340 mV for codes 0 to 3
(30.1, 20.9, 17.6, 24.6 dB), which follows the order of the effective feedback resistances.

## Requirements

- ngspice 42 (tested), Python 3 with `numpy` and `scipy` (`pip install -r requirements.txt`)
- Sky130 device models: `git clone https://github.com/google/skywater-pdk-libs-sky130_fd_pr`
- Environment variables: `SKY130PR=/path/to/that/clone` (required), `SIMTMP=/some/tmp/dir` (optional scratch directory)
- Run every script from its own directory: each directory has a `.spiceinit` that ngspice picks up from the working directory.

## Quick start

```
export SKY130PR=/path/to/skywater-pdk-libs-sky130_fd_pr
cd v2/sim && python3 smoke_test.py      # expects about 25.5 dB
```

## Reproducing the v2 results (`v2/sim/`)

| Script | What it does |
|---|---|
| `design.py`, `sizing.py` | Input-resistor design (`rin_design.json`) and device sizing |
| `pvt.py`, `analyze_pvt.py` | Gain, step size, input impedance over 5 process corners, 3 supplies, 4 temperatures |
| `sims2.py` | High-pass corners vs coupling capacitor and code, low-pass corners vs feedback capacitor, R/C corner runs, input-referred noise, enable/power-down current |
| `thd.py` | THD at the corners |
| `gaps.py`, `fh.py` | Settling after enable, load and THD gap-closing runs, upper corner |
| `bias_sweep.py` | Bias voltage and supply current over PVT |
| `make_plots.py` | Summary plots written to `results/plots/` (gain vs frequency and vs code, high-pass and upper corners, noise, enable settling); simulates what it needs, about 3 minutes on 2 cores, then reuses `plot_cache.pkl` (`--fresh` to re-simulate) |
| `run_rest.py`, `rerun30.py`, `rerun50.py`, `rerun100.py` | Re-runs for coupling-capacitor bank changes (the bank is `HPC` in `v2.py`; the current bank is 10/30/50 pF) |

Scripts write `.pkl`/`.json` result files into the working directory; these are not committed (they can be regenerated).
`pvt.py`/`analyze_pvt.py` were run in an earlier session and were not re-run when this repository was assembled.
Checked in this repository layout: `smoke_test.py`, `make_plots.py`, `rerun30.py`, `v1/sim/v1_overlay.py`, `v1/sim/v1val2.py`.
The plots show pre-layout typical-corner or stated-corner results; the 100 kHz point in the noise plot is the spec point, and the settling plot is for code 0.

## Reproducing the v1 comparison (`v1/sim/`)

```
cd v1/sim
python3 v1val2.py       # schematic with the real mux, 4 codes
python3 v1_overlay.py   # post-layout extracted netlist, 100 nF coupling, 1 Mohm || 24 pF load (AD3 input)
```

Proposal Figures 1 and 2 were produced separately from these scripts.

## License

Apache-2.0 (see `LICENSE`).
