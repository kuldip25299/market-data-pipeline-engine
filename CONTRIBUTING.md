# Contributing

Thank you for considering a contribution. This repository is primarily a
teaching resource, so contributions are judged on clarity as much as
correctness.

## Ground Rules

1. **Explain WHY, not just HOW.** If you add a feature or optimization,
   the accompanying docstring/comment/doc page must explain the problem
   it solves, not just what the code does mechanically.
2. **No premature optimization.** If you're proposing a performance
   change, include a benchmark (before/after) proving there was a real
   bottleneck. See `docs/05_performance_problem.md` for the standard
   we hold ourselves to.
3. **Keep files under ~200 lines.** If a file is growing past that,
   it's usually a sign it should be split into two well-named modules.
4. **Every public function needs type hints and a docstring.**

## Local Development Setup

```bash
git clone https://github.com/<your-username>/01-market-data-pipeline-engine.git
cd 01-market-data-pipeline-engine
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,charts]"
```

## Running Checks Before You Submit a PR

```bash
ruff check .
black --check .
mypy market_pipeline
pytest -m "not stress"      # fast suite
pytest                       # full suite, including stress tests
```

## Submitting a Pull Request

1. Fork the repository and create a branch from `main`.
2. Make your change, including tests and doc updates.
3. Ensure all checks above pass locally.
4. Open a PR using the provided template, describing the problem and
   your solution, and linking any relevant benchmark output.

## Reporting Bugs / Requesting Features

Please use the issue templates under `.github/ISSUE_TEMPLATE/`. Include
your Python version and OS -- performance characteristics discussed in
this repo can vary meaningfully across platforms.
