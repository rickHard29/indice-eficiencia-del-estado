"""Interfaz de línea de comandos para la adquisición de datos del IEE."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .ingestion import IngestionError, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Descarga y normaliza las APIs oficiales del piloto IEE."
    )
    parser.add_argument("--manifest", default="config/downloads.toml")
    parser.add_argument("--raw-dir", default="data/raw/official")
    parser.add_argument("--processed", default="data/processed/pilot_observations.csv")
    parser.add_argument("--provenance", default="data/interim/pilot_provenance.json")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-bytes", type=int, default=100_000_000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_pipeline(
            args.manifest,
            raw_dir=args.raw_dir,
            processed_path=args.processed,
            provenance_path=args.provenance,
            timeout=args.timeout,
            max_bytes=args.max_bytes,
        )
    except IngestionError as error:
        parser.exit(1, f"Error de adquisición: {error}\n")

    print(
        f"{result.observation_count} observaciones de {result.series_count} series; "
        f"SHA-256 {result.processed_sha256}"
    )
    print(f"Datos: {result.processed_path}")
    print(f"Procedencia: {result.provenance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
