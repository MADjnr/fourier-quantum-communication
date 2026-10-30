# IEEE-style research manuscript

**Fourier-Domain Spatial-Mode Conditioning for Coherent Optical Communication: A Reproducible Numerical Study**  
**Authors:** Afam Madu and Tofayel Karim

- [Read the compiled paper](main.pdf)
- [Editable LaTeX source](main.tex)
- [Verification and evidence mapping](VERIFICATION.md)
- [Six-page classroom speaking script (PDF)](classroom-presentation-script.pdf) — beginner-friendly story, analogies, and speaking cues for the ten archived figures and the two new investigation figures; [editable source](classroom-presentation-script.tex). Read the paragraphs aloud while displaying the paper's figures; bracketed directions are presenter actions.

The paper uses the actual `IEEEtran` journal class, a two-column layout, numbered equations/references, and evidence tables. It combines the archived baseline with a separately identified spectral-amplitude ceiling investigation. It is a research manuscript, **not an IEEE publication, accepted submission, or externally peer-reviewed article**. No affiliations, emails, funding statements, or author-contribution claims were invented. Venue-specific requirements and author approval remain necessary before submission.

## Scientific reading order

| Paper figure | Original asset | Role in the argument |
|---|---|---|
| 1 | `01_architecture` | Optical architecture and classical/quantum boundary |
| 2 | `02_fields` | Source, pre-mask Fourier field, and detector field |
| 3 | `03_comparison` | Three representative correction choices |
| 4 | `04_mask` | Selected continuous phase mask |
| 5 | `05_learning` | Training and validation-only checkpoint selection |
| 6 | `06_robustness` | Fixed-mask tolerance scan, followed by loss limits |
| 7 | `10_quantum` | Independent Gaussian moment check before receiver interpretation |
| 8 | `07_homodyne` | Unconditional, residual, conditional, and scatter statistics |
| 9 | `08_variance` | Theory/Monte Carlo variance and uncertainty |
| 10 | `09_snr` | SNR and the complete efficiency budget |

The original ten images are included directly from `../results/figures/`; the two new figures come from `../investigations/phase_limit/output/figures/`. No original plots, numerical arrays, metrics, or simulation source code were altered. Manuscript numbering is sequential even though the preserved filenames retain their original generation order.

| New paper figure | Investigation asset | Role |
|---|---|---|
| 11 | `01_limit_diagnosis` | Fresh paired comparison, nominal ablations, spectral mismatch, jitter bound |
| 12 | `02_architecture_and_controls` | Two-plane design, paired inputs, added loss, matched controls, seed blocks |

## What the new investigation changes

The archived 24-input result did not demonstrate trained superiority over analytic correction. The nominal analytic overlap **0.452898099** already saturates the single-Fourier-plane ceiling: phase adjustment there cannot reshape spectral magnitudes. A second phase screen at the input/image plane removes mean tilt and quadratic phase before the transform; a Fourier-plane ramp removes mean displacement. On **1,280 fresh inputs**, fixed analytic two-plane mean coupled power is **0.948633**, versus **0.449020** for one plane, with paired gain CI **[0.495002, 0.504224]**. These winning masks are analytic, not learned.

The new evidence also includes tiny matched-training gains, convergence checks and a residual jitter bound. Primary architecture comparisons and exploratory follow-up controls are distinct. See the [investigation reading/reproduction guide](../investigations/phase_limit/README.md), [full report](../investigations/phase_limit/REPORT.md), and [panel guide](../docs/FIGURE_GUIDE.md). The old reports remain archival records, not summaries of the expanded study.

## Build

From this directory, with [Tectonic](https://tectonic-typesetting.github.io/) installed:

```sh
tectonic --keep-logs main.tex
# Build the separate speaking script:
tectonic --keep-logs classroom-presentation-script.tex
```

The committed PDF was built with Tectonic 0.17.0. Its first build downloads the TeX bundle, IEEEtran, fonts, and packages into a local cache; later builds can reuse that cache. The source also uses standard packages suitable for a conventional TeX installation containing IEEEtran (run `pdflatex main.tex` twice). Only the Tectonic build was exercised for this delivery. References are embedded in the source; BibTeX is not needed. Compile from `paper/` so relative figure paths resolve.

## Scope

The paper retains the archived positive improvement over no correction and lack of demonstrated trained superiority in that small test, while adding the strong two-plane analytic architecture result and the small fresh one-plane training gains. Verification is numerical, not experimental. Passive phase conditioning does not reduce vacuum shot noise, restore lost photons, establish fabrication readiness, or calculate a secret-key rate. Limitations and provenance boundaries are explicit.
