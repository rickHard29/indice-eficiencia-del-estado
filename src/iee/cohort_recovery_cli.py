"""Interfaz para prioridades de recuperación de cohorte v0.3."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .cohort_recovery import CohortRecoveryError, run_cohort_recovery


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prioriza cobertura experimental; no calcula un ranking ni completa datos."
    )
    parser.add_argument("--config", default="config/cohort_recovery_v0.3.toml")
    parser.add_argument("--output", default="data/processed/cohort_recovery_v0.3.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_cohort_recovery(args.config, output_path=args.output)
    except CohortRecoveryError as error:
        parser.exit(1, f"Error de recuperación de cohorte: {error}\n")
    print(f"{result['countries_needed']} países por recuperar para alcanzar la meta.")
    print("Puntajes y ranking: no calculados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
