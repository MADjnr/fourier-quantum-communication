# Official references and installed API evidence

Verified with `curl -L --max-time 20` during this remediation: all three URLs returned HTTP 200. Stable SF URLs redirect to latest; these mutable documentation pages are not an environment lock.

- TorchOptics official documentation: https://torchoptics.readthedocs.io/en/latest/ — installed **torchoptics 0.4.0**, PyTorch **2.5.1+cpu**. Core reference checks use `torchoptics.Field`, normalization/power and propagation APIs; production 4f remains a sampled Fourier operator, not a complete TorchOptics relay.
- Strawberry Fields official documentation: https://strawberryfields.readthedocs.io/en/stable/ — installed **StrawberryFields 0.23.0** in `.venv-sf`.
- Official loss-channel API: https://strawberryfields.readthedocs.io/en/stable/code/api/strawberryfields.ops.LossChannel.html — executed API: `sf.Program(1)`, `ops.Coherent`, `ops.LossChannel`, `sf.Engine('gaussian').run(program).state`, `state.means()`, `state.cov()`, with `sf.hbar=2`.

Exact distributions (including transitive dependencies) are captured in `requirements.txt` and `requirements-sf.txt` using `uv --no-config pip freeze`. Runtime SF version evidence is returned in the validation metrics; installing SF does not retroactively change archived results. Gaussian samples in the figures remain NumPy samples even when SF independently validates the moments.
