PYTHON ?= .venv/bin/python
CONFIG ?= configs/baseline.yaml
OUTPUT ?= results
export MPLBACKEND = Agg
.PHONY: setup test run report all
setup:
	bash scripts/setup_linux.sh
test:
	$(PYTHON) -m pytest -q
run:
	$(PYTHON) -m src.run --config $(CONFIG) --output $(OUTPUT)
report:
	$(PYTHON) -m src.run --output $(OUTPUT) --report-only
all: test run
