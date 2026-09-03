"""Interfaz para preparar el paquete de revisión metodológica v0.4."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .review_bundle import ReviewBundleError, run_review_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepara artefactos para revisión; no aprueba metodología ni calcula ranking."
    )
    parser.add_argument("--config", default="config/review_bundle_v0.4.toml")
    parser.add_argument("--output", default="data/processed/review_bundle_v0.4.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_review_bundle(args.config, output_path=args.output)
    except ReviewBundleError as error:
        parser.exit(1, f"Error de paquete de revisión: {error}\n")
    print(f"{len(result['artifacts'])} artefactos preparados para revisión.")
    print("Aprobación, puntajes y ranking: no registrados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
