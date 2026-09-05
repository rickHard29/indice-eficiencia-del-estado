"""CLI para la prueba de sensibilidad del ranking exploratorio."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .results_ranking_sensitivity import ResultsRankingSensitivityError, run_results_ranking_sensitivity


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prueba la sensibilidad del ranking exploratorio, no del IEE.")
    parser.add_argument("--config", default="config/results_ranking_sensitivity_v0.1.toml")
    parser.add_argument("--output", default="data/processed/results_ranking_sensitivity_v0.1.json")
    args = parser.parse_args(argv)
    try:
        result = run_results_ranking_sensitivity(args.config, output_path=args.output)
    except ResultsRankingSensitivityError as error:
        parser.exit(1, f"Error de sensibilidad: {error}\n")
    print(f"Sensibilidad exploratoria: {len(result['rank_stability'])} países y {len(result['scenarios'])} escenarios.")
    print("IEE oficial: no calculado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
