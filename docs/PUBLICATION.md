# Standalone public export and provenance

This repository contains the full simulation implementation, exact dependency version freezes, tests, scientific documentation, and archived numerical results. It was copied into a separate standalone folder; the original local workspace was preserved.

## Publication boundary

Included: source, configuration, scripts, test suite, internal engineering reviews, reports, ten PNG/SVG figure pairs, numerical arrays, metrics, logs, and artifact manifest.

Excluded: virtual environments, bytecode/test caches, unrelated parent-workspace files, private collaboration documentation and third-party PDF attachments. All scientific dependencies are installed from pinned requirements rather than redistributed. No software license was inferred from publication permission.

## What changed in the exported baseline?

- The README was replaced with an evidence-linked scientific narrative and reproduction instructions.
- A standalone `.gitignore` tracks the published `results/` but ignores new `runs/` and environment files.
- Absolute local interpreter/test paths and a hostname were removed from publication metadata/logs. `manifest.json` documents those redactions and updates the two affected log checksums.
- The stale report-only `render_manifest.json` from an earlier rendering was omitted: the final simulation's `manifest.json` is the applicable record.
- A standard-library-only `scripts/verify_artifacts.py` verifies all recorded artifacts.
- Numerical arrays, masks, metrics, configuration, figures, CSV, and reports remain byte-for-byte identical to the completed baseline.

The historical `git_revision` in the simulation manifest refers to a parent workspace at execution time, with `git_dirty: true`; it does not identify the implementation source. The standalone repository's first commit records the actual exported source and evidence. No claim is made that the old revision alone can reproduce these results.

## Scientific verification boundary

The archived run passed 41 automated tests. Internal specification and code reviews assessed the ideal sampled focal-plane model. These are engineering checks, not peer review or experimental validation. The README distinguishes analytical identities, numerical checks, Monte Carlo observations, confidence intervals and untested physical assumptions.

The main environment does not install Strawberry Fields. A separate `.venv-sf` executes it, and the actual backend versions/errors are recorded in `results/metrics.json` under `quantum_validation`. Consequently `strawberryfields: not installed` in the main environment package manifest is not a fallback claim.

The original numerical outputs were not rerun just to publish them. The exported tests and checksum validation were rerun; exact original artifact preservation was checked against the source workspace. For a new simulation, use `--output runs/reproduction` to preserve the archived evidence.
