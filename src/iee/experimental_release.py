"""Interfaz para el recibo de preparación experimental v0.2."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .experimental_readiness import ExperimentalReadinessError, run_experimental_readiness


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Empaqueta evidencia experimental; no calcula un ranking ni un IEE oficial."
    )
    parser.add_argument("--config", default="config/experimental_release_v0.2.toml")
    parser.add_argument("--output", default="data/processed/experimental_release_v0.2.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_experimental_readiness(args.config, output_path=args.output)
    except ExperimentalReadinessError as error:
        parser.exit(1, f"Error de preparación experimental: {error}\n")
    print(f"{result['dimensions_with_experimental_track']} dimensiones verificadas.")
    print("IEE general y ranking: no calculados")
    print("Publicación oficial: bloqueada por controles metodológicos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
