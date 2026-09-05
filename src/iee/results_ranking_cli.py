"""CLI para el ranking exploratorio de resultados."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .results_ranking import ResultsRankingError, run_results_ranking


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publica un ranking exploratorio de resultados, no el IEE.")
    parser.add_argument("--config", default="config/results_ranking_v0.1.toml")
    parser.add_argument("--output", default="data/processed/results_ranking_v0.1.json")
    args = parser.parse_args(argv)
    try:
        result = run_results_ranking(args.config, output_path=args.output)
    except ResultsRankingError as error:
        parser.exit(1, f"Error de ranking exploratorio: {error}\n")
    print(f"Ranking exploratorio de resultados: {len(result['ranking'])} países.")
    print("IEE oficial: no calculado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
