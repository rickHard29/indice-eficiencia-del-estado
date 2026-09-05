"""Interfaz para cerrar el corte común vigente sin agregación."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .current_cohort_release import CurrentCohortReleaseError, run_current_cohort_release


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cierra la cohorte común experimental; no genera puntajes ni ranking."
    )
    parser.add_argument("--config", default="config/current_cohort_release_v1.toml")
    parser.add_argument("--output", default="data/processed/current_cohort_release_v1.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_current_cohort_release(args.config, output_path=args.output)
    except CurrentCohortReleaseError as error:
        parser.exit(1, f"Error de cierre de cohorte: {error}\n")
    current = result["current_common_cohort"]
    print(f"Cohorte común cerrada: {current['complete_countries']} países.")
    print("IEE general y ranking: no calculados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
