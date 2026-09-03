"""Interfaz de línea de comandos para el diagnóstico integrado de seguridad."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .security_role_panel import SecurityRolePanelError, run_security_role_panel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Integra cobertura de resultado, equidad e insumo de seguridad."
    )
    parser.add_argument("--config", default="config/security_role_integration_v2.5.toml")
    parser.add_argument("--result-observations", default="data/processed/v25_results.csv")
    parser.add_argument("--result-provenance", default="data/interim/v25_results.json")
    parser.add_argument("--equity-observations", default="data/processed/v25_equity.csv")
    parser.add_argument("--equity-provenance", default="data/interim/v25_equity.json")
    parser.add_argument("--input-observations", default="data/processed/v25_inputs.csv")
    parser.add_argument("--input-provenance", default="data/interim/v25_inputs.json")
    parser.add_argument("--panel", default="data/processed/v25_security_role_panel.csv")
    parser.add_argument("--gate", default="data/processed/v25_security_role_gate.json")
    parser.add_argument("--provenance", default="data/interim/v25_security_role_provenance.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_security_role_panel(
            args.config,
            result_observations_path=args.result_observations,
            result_provenance_path=args.result_provenance,
            equity_observations_path=args.equity_observations,
            equity_provenance_path=args.equity_provenance,
            input_observations_path=args.input_observations,
            input_provenance_path=args.input_provenance,
            panel_path=args.panel,
            gate_path=args.gate,
            provenance_path=args.provenance,
        )
    except SecurityRolePanelError as error:
        parser = build_parser()
        parser.exit(1, f"Error de integración: {error}\n")
    print(f"{result.complete_roles} países con los tres roles de {result.panel_count}")
    print(f"Panel: {result.panel_path}")
    print(f"Puerta: {result.gate_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
