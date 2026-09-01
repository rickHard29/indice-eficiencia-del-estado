from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.experimental_frontier import load_estimator_config
from iee.frontier_panel import load_frontier_panel_config
from iee.ingestion import load_download_manifest, run_pipeline


class AdministrationV11Tests(unittest.TestCase):
    def test_frontier_contract_preserves_the_temporal_gap_and_official_block(self) -> None:
        root = Path(__file__).resolve().parents[1]
        panel = load_frontier_panel_config(root / "config" / "frontier_panel_v1.1.toml")
        estimator = load_estimator_config(root / "config" / "frontier_estimator_v1.1.toml")

        self.assertEqual(panel.version, "1.1")
        self.assertEqual(panel.status, "experimental-not-for-publication")
        self.assertEqual(len(panel.countries), 38)
        dimension = panel.dimensions[0]
        self.assertEqual(dimension.id, "administracion")
        self.assertEqual(dimension.outcome_periods, (2024,))
        self.assertEqual(dimension.input_periods, (2019, 2020, 2021))
        self.assertEqual(dimension.input_status_required, "conditional")
        self.assertEqual(estimator.version, "1.1")
        self.assertEqual(estimator.rules[0].outcome_indicator_id, "ADM-RES-01")
        self.assertEqual(estimator.rules[0].bound_status, "natural_scale")

    def test_manual_pdf_control_materializes_the_oecd38_osi_panel_offline(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest_path = root / "config" / "downloads_admin_v1.1.toml"
        manifest = load_download_manifest(manifest_path)

        self.assertEqual(manifest.version, "1.1")
        self.assertEqual(len(manifest.countries), 38)
        self.assertEqual(manifest.series, ())
        self.assertEqual(manifest.manual_control_ids, ("ADM-RES-01",))

        with TemporaryDirectory() as temporary:
            directory = Path(temporary)

            def forbidden_fetcher(*_args: object, **_kwargs: object) -> object:
                raise AssertionError("el control manual no debe llamar a la red")

            result = run_pipeline(
                manifest_path,
                raw_dir=directory / "raw",
                processed_path=directory / "observations.csv",
                provenance_path=directory / "provenance.json",
                fetcher=forbidden_fetcher,
                retrieved_at="2026-08-25T00:00:00+00:00",
            )

            self.assertEqual(result.observation_count, 38)
            self.assertEqual(result.series_count, 1)
            self.assertEqual(result.raw_resource_count, 0)
            with (directory / "observations.csv").open(newline="", encoding="utf-8") as file:
                rows = {row["entity"]: row for row in csv.DictReader(file)}
            self.assertEqual(Decimal(rows["COL"]["value"]), Decimal("0.7521"))
            self.assertEqual(Decimal(rows["USA"]["value"]), Decimal("0.9136"))
            self.assertTrue(all(row["observation_kind"] == "manual_control" for row in rows.values()))

            receipt = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(
                receipt["series_counts"],
                {"automatic": 0, "manual_control": 1, "materialized": 1},
            )
            self.assertEqual(receipt["manual_controls"]["indicator_ids"], ["ADM-RES-01"])


if __name__ == "__main__":
    unittest.main()
