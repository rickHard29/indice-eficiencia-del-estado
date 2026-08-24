"""Interfaz para ejecutar el diagnóstico experimental del piloto IEE."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .experimental_scoring import ExperimentalScoringError, run_experiment
from .ingestion import IngestionError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Calcula perfiles diagnósticos experimentales y aplica los bloqueos "
            "de publicación del piloto IEE."
        )
    )
    parser.add_argument("--config", default="config/scoring_experiment.toml")
    parser.add_argument("--observations", default="data/processed/pilot_observations.csv")
    parser.add_argument(
        "--ingestion-provenance", default="data/interim/pilot_provenance.json"
    )
    parser.add_argument(
        "--indicator-output",
        default="data/processed/iee_experimental_indicator_scores.csv",
    )
    parser.add_argument(
        "--diagnostic-output",
        default="data/processed/iee_experimental_dimension_diagnostics.csv",
    )
    parser.add_argument(
        "--sensitivity-output",
        default="data/processed/iee_experimental_sensitivity.csv",
    )
    parser.add_argument(
        "--context-output",
        default="data/processed/iee_experimental_input_context.csv",
    )
    parser.add_argument(
        "--provenance-output",
        default="data/interim/iee_experimental_provenance.json",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_experiment(
            args.config,
            observations_path=args.observations,
            ingestion_provenance_path=args.ingestion_provenance,
            indicator_path=args.indicator_output,
            diagnostic_path=args.diagnostic_output,
            sensitivity_path=args.sensitivity_output,
            context_path=args.context_output,
            provenance_path=args.provenance_output,
        )
    except (ExperimentalScoringError, IngestionError) as error:
        parser.exit(1, f"Error de diagnóstico: {error}\n")

    print(
        f"{result.indicator_count} perfiles de indicador y "
        f"{result.diagnostic_count} diagnósticos generados."
    )
    for entity, score in sorted(result.diagnostic_composite.items()):
        print(f"{entity}: compuesto diagnóstico de resultados = {score:.2f}")
    print("IEE general: no calculado")
    print("Publicación y ranking: bloqueados por los controles metodológicos")
    print(f"Procedencia: {result.provenance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
