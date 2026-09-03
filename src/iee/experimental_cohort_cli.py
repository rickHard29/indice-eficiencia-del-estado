"""Interfaz para el control de cohorte común experimental v0.3."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .experimental_cohort import ExperimentalCohortError, run_experimental_cohort


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mide la cohorte común experimental; no calcula puntajes ni ranking."
    )
    parser.add_argument("--config", default="config/experimental_cohort_v0.3.toml")
    parser.add_argument("--output", default="data/processed/experimental_cohort_v0.3.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_experimental_cohort(args.config, output_path=args.output)
    except ExperimentalCohortError as error:
        parser.exit(1, f"Error de cohorte experimental: {error}\n")
    common = result["common_cohort"]
    print(f"{common['complete_countries']} países en la intersección común.")
    print("IEE general y ranking: no calculados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
