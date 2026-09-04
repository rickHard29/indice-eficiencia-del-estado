from __future__ import annotations

import argparse
from collections.abc import Sequence

from .recovery_candidates import RecoveryCandidatesError, run_recovery_candidates


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Registra rutas candidatas; no adopta observaciones.")
    parser.add_argument("--config", default="config/recovery_candidates_v0.6.toml")
    parser.add_argument("--output", default="data/processed/recovery_candidates_v0.6.json")
    args = parser.parse_args(argv)
    try:
        result = run_recovery_candidates(args.config, output_path=args.output)
    except RecoveryCandidatesError as error:
        parser.exit(1, f"Error de candidatas: {error}\n")
    print(f"{len(result['candidates'])} rutas; {result['adopted_observations']} observaciones adoptadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
