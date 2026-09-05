from __future__ import annotations

import argparse
from collections.abc import Sequence

from .recovery_resolution import RecoveryResolutionError, run_recovery_resolution


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cierra rutas de recuperación sin adoptar datos.")
    parser.add_argument("--config", default="config/recovery_resolution_v0.7.toml")
    parser.add_argument("--output", default="data/processed/recovery_resolution_v0.7.json")
    args = parser.parse_args(argv)
    try:
        result = run_recovery_resolution(args.config, output_path=args.output)
    except RecoveryResolutionError as error:
        parser.exit(1, f"Error de resolución: {error}\n")
    print(f"{len(result['resolutions'])} rutas resueltas; {result['adopted_observations']} observaciones adoptadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
