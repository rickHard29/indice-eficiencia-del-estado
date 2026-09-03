"""Interfaz para el cribado de fuentes de recuperación v0.5."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .recovery_source_screen import RecoverySourceScreenError, run_recovery_source_screen


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Criba fuentes candidatas; no rellena ni puntúa.")
    parser.add_argument("--config", default="config/recovery_source_screen_v0.5.toml")
    parser.add_argument("--output", default="data/processed/recovery_source_screen_v0.5.json")
    args = parser.parse_args(argv)
    try:
        result = run_recovery_source_screen(args.config, output_path=args.output)
    except RecoverySourceScreenError as error:
        parser.exit(1, f"Error de cribado de fuentes: {error}\n")
    print(f"{len(result['candidates'])} candidatas evaluadas; {result['adopted_candidates']} adoptadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
