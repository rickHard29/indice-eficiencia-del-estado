"""Interfaz para el núcleo común de resultados comparables."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .outcomes_core_cohort import OutcomesCoreCohortError, run_outcomes_core_cohort


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Mide resultados comunes; no calcula eficiencia ni ranking."
    )
    parser.add_argument("--config", default="config/outcomes_core_cohort_v1.toml")
    parser.add_argument("--output", default="data/processed/outcomes_core_cohort_v1.json")
    args = parser.parse_args(argv)
    try:
        result = run_outcomes_core_cohort(args.config, output_path=args.output)
    except OutcomesCoreCohortError as error:
        parser.exit(1, f"Error de núcleo de resultados: {error}\n")
    core = result["outcomes_core"]
    print(f"Núcleo común de resultados: {core['complete_countries']} países.")
    print("IEE general y ranking: no calculados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
