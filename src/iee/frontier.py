"""Interfaz para preparar el panel experimental de frontera v0.3."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .frontier_panel import FrontierPanelError, run_frontier_panel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Une resultados e insumos en un panel v0.3; no calcula un IEE oficial."
    )
    parser.add_argument("--config", default="config/frontier_panel_v0.3.toml")
    parser.add_argument("--result-observations", default="data/processed/v03_result_observations.csv")
    parser.add_argument("--result-provenance", default="data/interim/v03_result_provenance.json")
    parser.add_argument("--input-observations", default="data/processed/v02_input_proxies.csv")
    parser.add_argument("--input-provenance", default="data/interim/v02_input_provenance.json")
    parser.add_argument("--panel-output", default="data/processed/v03_frontier_panel.csv")
    parser.add_argument("--gates-output", default="data/processed/v03_frontier_gates.csv")
    parser.add_argument("--provenance-output", default="data/interim/v03_frontier_provenance.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_frontier_panel(
            args.config,
            result_observations_path=args.result_observations,
            result_provenance_path=args.result_provenance,
            input_observations_path=args.input_observations,
            input_provenance_path=args.input_provenance,
            panel_path=args.panel_output,
            gates_path=args.gates_output,
            provenance_path=args.provenance_output,
        )
    except FrontierPanelError as error:
        parser.exit(1, f"Error de panel de frontera: {error}\n")
    print(f"{result.panel_count} filas de panel y {result.gate_count} gates generados.")
    print("IEE general: no calculado")
    print("Publicación y ranking: bloqueados por los controles metodológicos")
    print(f"Procedencia: {result.provenance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
