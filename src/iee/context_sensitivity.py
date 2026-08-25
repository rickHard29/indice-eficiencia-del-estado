"""Interfaz de línea de comandos para sensibilidades de contexto v0.4."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .experimental_context import ContextSensitivityError, run_context_sensitivity


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compara fronteras experimentales con controles de contexto separados."
    )
    parser.add_argument("--config", default="config/context_sensitivity_v0.4.toml")
    parser.add_argument("--panel", default="data/processed/v03_frontier_panel.csv")
    parser.add_argument("--gates", default="data/processed/v03_frontier_gates.csv")
    parser.add_argument("--panel-provenance", default="data/interim/v03_frontier_provenance.json")
    parser.add_argument("--context", default="data/processed/v04_context_observations.csv")
    parser.add_argument("--context-provenance", default="data/interim/v04_context_provenance.json")
    parser.add_argument(
        "--rows-output", default="data/processed/v04_context_frontier_sensitivity.csv"
    )
    parser.add_argument(
        "--models-output", default="data/processed/v04_context_frontier_models.csv"
    )
    parser.add_argument(
        "--provenance-output", default="data/interim/v04_context_frontier_provenance.json"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_context_sensitivity(
            args.config,
            panel_path=args.panel,
            gates_path=args.gates,
            panel_provenance_path=args.panel_provenance,
            context_path=args.context,
            context_provenance_path=args.context_provenance,
            rows_path=args.rows_output,
            models_path=args.models_output,
            provenance_path=args.provenance_output,
        )
    except ContextSensitivityError as error:
        parser.exit(1, f"Error de sensibilidad de contexto: {error}\n")
    print(f"{result.row_count} comparaciones y {result.model_count} modelos de contexto generados.")
    print("IEE general y ranking: no calculados")
    print(f"Procedencia: {result.provenance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
