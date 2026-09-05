"""CLI para publicar CSV abiertos del ranking exploratorio."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .results_ranking_publication import ResultsRankingPublicationError, run_results_ranking_publication


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publica CSV del ranking exploratorio, no del IEE oficial.")
    parser.add_argument("--config", default="config/results_ranking_publication_v0.1.toml")
    parser.add_argument("--ranking-output", default="docs/publication/results-ranking-v0.1.csv")
    parser.add_argument("--stability-output", default="docs/publication/results-ranking-stability-v0.1.csv")
    args = parser.parse_args(argv)
    try:
        result = run_results_ranking_publication(
            args.config,
            ranking_output_path=args.ranking_output,
            stability_output_path=args.stability_output,
        )
    except ResultsRankingPublicationError as error:
        parser.exit(1, f"Error de publicación exploratoria: {error}\n")
    print(f"CSV exploratorios publicados: {result['countries']} países.")
    print("IEE oficial: no calculado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
