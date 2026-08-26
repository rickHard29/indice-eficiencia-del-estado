"""Interfaz para estimar la frontera cuantílica experimental v0.3."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .experimental_frontier import ExperimentalFrontierError, run_experimental_frontier


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Estima fronteras experimentales por dimensión; no calcula un IEE oficial."
    )
    parser.add_argument("--config", default="config/frontier_estimator_v0.3.toml")
    parser.add_argument("--panel", default="data/processed/v03_frontier_panel.csv")
    parser.add_argument("--gates", default="data/processed/v03_frontier_gates.csv")
    parser.add_argument(
        "--panel-provenance", default="data/interim/v03_frontier_provenance.json"
    )
    parser.add_argument(
        "--estimates-output",
        default="data/processed/v03_experimental_frontier_estimates.csv",
    )
    parser.add_argument(
        "--models-output", default="data/processed/v03_experimental_frontier_models.csv"
    )
    parser.add_argument(
        "--sensitivity-output",
        default="data/processed/v03_experimental_frontier_sensitivity.csv",
    )
    parser.add_argument(
        "--provenance-output",
        default="data/interim/v03_experimental_frontier_provenance.json",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_experimental_frontier(
            args.config,
            panel_path=args.panel,
            gates_path=args.gates,
            panel_provenance_path=args.panel_provenance,
            estimates_path=args.estimates_output,
            models_path=args.models_output,
            sensitivity_path=args.sensitivity_output,
            provenance_path=args.provenance_output,
        )
    except ExperimentalFrontierError as error:
        parser.exit(1, f"Error de frontera experimental: {error}\n")
    print(
        f"{result.estimate_count} perfiles, {result.model_count} modelos y "
        f"{result.sensitivity_count} filas de sensibilidad generados."
    )
    print("IEE general: no calculado")
    print("Publicación y ranking: bloqueados por los controles metodológicos")
    print(f"Procedencia: {result.provenance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
