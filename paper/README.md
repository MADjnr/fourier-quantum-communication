# IEEE-style research manuscript

**Fourier-Domain Spatial-Mode Conditioning for Coherent Optical Communication: A Reproducible Numerical Study**  
**Authors:** Afam Madu and Tofayel Karim

- [Read the compiled paper](main.pdf)
- [Editable LaTeX source](main.tex)
- [Verification and evidence mapping](VERIFICATION.md)
- [Four-page classroom speaking script (PDF)](classroom-presentation-script.pdf) — beginner-friendly story, analogies, and speaking cues for all ten figures in manuscript order; [editable source](classroom-presentation-script.tex). Read the paragraphs aloud while displaying the paper's figures; bracketed directions are presenter actions.

The paper uses the actual `IEEEtran` journal class, a two-column layout, numbered equations/references, ten figures, and four evidence tables. It is a research manuscript, **not an IEEE publication, accepted submission, or externally peer-reviewed article**. No affiliations, emails, funding statements, or author-contribution claims were invented. Venue-specific requirements and author approval remain necessary before submission.

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

All images are included directly from `../results/figures/`; no original plots, numerical arrays, metrics, or source code were altered. Manuscript numbering is sequential even though the preserved filenames retain their original generation order.

## Build

From this directory, with [Tectonic](https://tectonic-typesetting.github.io/) installed:

```sh
tectonic --keep-logs main.tex
# Build the separate four-page speaking script:
tectonic --keep-logs classroom-presentation-script.tex
```

The committed PDF was built with Tectonic 0.17.0. Its first build downloads the TeX bundle, IEEEtran, fonts, and packages into a local cache; later builds can reuse that cache. The source also uses standard packages suitable for a conventional TeX installation containing IEEEtran (run `pdflatex main.tex` twice). Only the Tectonic build was exercised for this delivery. References are embedded in the source; BibTeX is not needed. Compile from `paper/` so relative figure paths resolve.

## Scope

The paper retains the positive improvement over no correction **and the absence of demonstrated superiority over analytic correction**. Verification is numerical, not experimental. Passive phase conditioning does not reduce vacuum shot noise, restore lost photons, establish fabrication readiness, or calculate a secret-key rate. Limitations and provenance boundaries are explicit.
