from __future__ import annotations

from decimal import Decimal
import io
import json
import os
from pathlib import Path
import socket
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import zipfile

from iee.ingestion import (
    _acquire_series,
    _atomic_write_publication,
    _validate_raw_targets,
    DownloadSpec,
    FetchedPayload,
    IngestionError,
    Observation,
    download_url,
    load_download_manifest,
    observations_to_csv,
    parse_oecd_percent_times_level,
    parse_oecd_pisa_xlsx,
    parse_oecd_ppp_per_capita,
    parse_oecd_ratio_csv,
    parse_oecd_ratio_times_level,
    parse_oecd_sdmx_csv,
    parse_world_bank_json,
    parse_world_bank_percent_times_level,
    run_pipeline,
    sha256_hex,
    validate_observations,
)


WB_JSON = (
    b'[{"page":1,"pages":1,"per_page":100,"total":4,'
    b'"lastupdated":"2026-07-13"},['
    b'{"countryiso3code":"COL","date":"2022","value":25.4},'
    b'{"countryiso3code":"COL","date":"2023","value":24.913442},'
    b'{"countryiso3code":"USA","date":"2022","value":6.383588},'
    b'{"countryiso3code":"USA","date":"2023","value":5.76340794}]]'
)


def pisa_xlsx_fixture() -> bytes:
    """Minimal XLSX fixture: numeric value, sampling caution and a missing value."""

    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            """<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"
            xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
            <sheets><sheet name=\"Table I.B1.4.1\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            """<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
            <Relationship Id=\"rId1\" Target=\"worksheets/sheet1.xml\"/></Relationships>""",
        )
        archive.writestr(
            "xl/sharedStrings.xml",
            """<sst xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
            <si><t>Colombia</t></si><si><t>United States*</t></si><si><t>m</t></si></sst>""",
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            """<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData>
            <row r=\"11\"><c r=\"A11\" t=\"s\"><v>0</v></c><c r=\"E11\"><v>72.5</v></c></row>
            <row r=\"12\"><c r=\"A12\" t=\"s\"><v>1</v></c><c r=\"E12\"><v>86.4</v></c></row>
            <row r=\"13\"><c r=\"A13\" t=\"s\"><v>2</v></c><c r=\"E13\" t=\"s\"><v>2</v></c></row>
            </sheetData></worksheet>""",
        )
    return payload.getvalue()


def make_spec(**overrides: object) -> DownloadSpec:
    values: dict[str, object] = {
        "resource_id": "seg-res-01",
        "indicator_id": "SEG-RES-01",
        "source_id": "UNODC-WDI",
        "source_status": "validated",
        "score_eligible": True,
        "adapter": "world_bank_json",
        "series_code": "VC.IHR.PSRC.P5",
        "url": "https://example.test/data",
        "direction": "lower",
        "unit": "Víctimas por 100.000 habitantes",
        "expected_entities": ("COL", "USA"),
        "expected_latest_year": {"COL": 2023, "USA": 2023},
        "expected_latest_value": {
            "COL": Decimal("24.913442"),
            "USA": Decimal("5.76340794"),
        },
        "latest_value_tolerance": Decimal("0.000001"),
        "minimum_observations_per_entity": 2,
    }
    values.update(overrides)
    return DownloadSpec(**values)  # type: ignore[arg-type]


class FakeResponse:
    def __init__(self, content: bytes, *, content_type: str = "application/json") -> None:
        self.content = content
        self.headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(content)),
            "ETag": '"fixture"',
        }

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self.content if size < 0 else self.content[:size]

    def geturl(self) -> str:
        return "https://example.test/final"


class IngestionParsingTests(unittest.TestCase):
    def test_sha256_uses_original_bytes(self) -> None:
        self.assertEqual(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )
        self.assertNotEqual(sha256_hex(b"a\n"), sha256_hex(b"a\r\n"))

    def test_download_returns_exact_bytes_and_metadata(self) -> None:
        calls: list[tuple[object, float]] = []

        def opener(request: object, *, timeout: float) -> FakeResponse:
            calls.append((request, timeout))
            return FakeResponse(WB_JSON)

        fetched = download_url(
            "https://example.test/data",
            accept="application/json",
            timeout=7.5,
            opener=opener,
        )

        self.assertEqual(fetched.content, WB_JSON)
        self.assertEqual(fetched.final_url, "https://example.test/final")
        self.assertEqual(fetched.etag, '"fixture"')
        self.assertEqual(calls[0][1], 7.5)

    def test_http_errors_are_wrapped(self) -> None:
        def opener(_request: object, *, timeout: float) -> FakeResponse:
            del timeout
            raise HTTPError("https://example.test", 429, "rate", {}, None)

        with self.assertRaisesRegex(IngestionError, "HTTP 429") as context:
            download_url(
                "https://example.test/data",
                accept="application/json",
                opener=opener,
            )
        self.assertIsInstance(context.exception.__cause__, HTTPError)

    def test_world_bank_json_is_typed_and_sorted(self) -> None:
        observations = parse_world_bank_json(WB_JSON, make_spec())

        self.assertEqual(len(observations), 4)
        self.assertEqual(observations[0].entity, "COL")
        self.assertEqual(observations[0].value, Decimal("25.4"))
        self.assertEqual(observations[-1].value, Decimal("5.76340794"))

    def test_pisa_xlsx_preserves_sampling_caution_and_skips_missing_values(self) -> None:
        spec = make_spec(
            adapter="oecd_pisa_xlsx",
            indicator_id="EDU-ACC-02",
            series_code="Coverage Index 3",
            direction="higher",
            unit="Porcentaje",
            expected_latest_year={"COL": 2022, "USA": 2022},
            expected_latest_value={"COL": Decimal("72.5"), "USA": Decimal("86.4")},
            minimum_observations_per_entity=1,
            reference_year=2022,
            worksheet="Table I.B1.4.1",
            entity_column="A",
            value_column="E",
            entity_aliases={"Colombia": "COL", "United States": "USA"},
        )

        observations = parse_oecd_pisa_xlsx(pisa_xlsx_fixture(), spec)

        self.assertEqual([(row.entity, row.period, row.value) for row in observations], [
            ("COL", 2022, Decimal("72.5")),
            ("USA", 2022, Decimal("86.4")),
        ])
        self.assertEqual(observations[1].observation_status, "source:sampling_caution")

    def test_world_bank_rejects_incomplete_pagination(self) -> None:
        payload = WB_JSON.replace(b'"pages":1', b'"pages":2', 1)
        with self.assertRaisesRegex(IngestionError, "paginada"):
            parse_world_bank_json(payload, make_spec())

    def test_oecd_csv_accepts_bom_and_has_deterministic_order(self) -> None:
        payload = (
            b"\xef\xbb\xbfREF_AREA,TIME_PERIOD,OBS_VALUE,UNIT_MULT,OBS_STATUS\n"
            b"USA,2023,1.85,0,A\n"
            b"COL,2023,2.23,0,A\n"
        )
        spec = make_spec(
            adapter="oecd_sdmx_csv",
            expected_latest_year={"COL": 2023, "USA": 2023},
            expected_latest_value={"COL": Decimal("2.23"), "USA": Decimal("1.85")},
            minimum_observations_per_entity=1,
        )

        observations = parse_oecd_sdmx_csv(payload, spec)

        self.assertEqual([row.entity for row in observations], ["COL", "USA"])
        self.assertEqual(observations[0].value, Decimal("2.23"))

    def test_oecd_xml_response_is_rejected(self) -> None:
        with self.assertRaisesRegex(IngestionError, "format=csvfile"):
            parse_oecd_sdmx_csv(b"<?xml version='1.0'?><data/>", make_spec())

    def test_oecd_ratio_requires_components_and_keeps_provisional_flag(self) -> None:
        numerator = (
            b"REF_AREA,TIME_PERIOD,OBS_VALUE,TRANSACTION,UNIT_MULT,CURRENCY,OBS_STATUS\n"
            b"COL,2024,2,D1,6,COP,A\nCOL,2024,3,P2,6,COP,A\n"
            b"USA,2024,4,D1,6,USD,A\nUSA,2024,2,P2,6,USD,A\n"
        )
        denominator = (
            b"REF_AREA,TIME_PERIOD,OBS_VALUE,UNIT_MULT,CURRENCY,OBS_STATUS\n"
            b"COL,2024,10,6,COP,P\nUSA,2024,12,6,USD,A\n"
        )
        spec = make_spec(
            adapter="oecd_ratio_csv",
            category_column="TRANSACTION",
            expected_categories=("D1", "P2"),
            scale=Decimal("100"),
            direction="input",
            score_eligible=False,
            source_status="conditional",
            expected_latest_year={"COL": 2024, "USA": 2024},
            expected_latest_value={"COL": Decimal("50"), "USA": Decimal("50")},
            minimum_observations_per_entity=1,
        )

        observations = parse_oecd_ratio_csv(numerator, denominator, spec)

        self.assertEqual(observations[0].value, Decimal("50"))
        self.assertEqual(observations[0].observation_status, "provisional")
        self.assertEqual(observations[1].value, Decimal("50"))

    def test_oecd_ppp_per_capita_uses_exact_country_year_join(self) -> None:
        expenditure = (
            b"REF_AREA,TIME_PERIOD,OBS_VALUE,UNIT_MULT,OBS_STATUS\n"
            b"COL,2024,100,6,A\nUSA,2024,200,6,A\n"
        )
        ppp = (
            b'[{"page":1,"pages":1},['
            b'{"countryiso3code":"COL","date":"2024","value":2},'
            b'{"countryiso3code":"USA","date":"2024","value":1}]]'
        )
        population = (
            b'[{"page":1,"pages":1},['
            b'{"countryiso3code":"COL","date":"2024","value":10000000},'
            b'{"countryiso3code":"USA","date":"2024","value":20000000}]]'
        )
        spec = make_spec(
            adapter="oecd_ppp_per_capita",
            direction="input",
            score_eligible=False,
            source_status="reserve",
            expected_latest_year={"COL": 2024, "USA": 2024},
            expected_latest_value={"COL": Decimal("5"), "USA": Decimal("10")},
            minimum_observations_per_entity=1,
        )

        observations = parse_oecd_ppp_per_capita(expenditure, ppp, population, spec)

        self.assertEqual([row.value for row in observations], [Decimal("5"), Decimal("10")])
        self.assertTrue(all(row.observation_kind == "derived" for row in observations))

    def test_world_bank_percent_times_constant_ppp_level(self) -> None:
        percentages = (
            b'[{"page":1,"pages":1},['
            b'{"countryiso3code":"COL","date":"2023","value":4},'
            b'{"countryiso3code":"USA","date":"2023","value":8}]]'
        )
        levels = (
            b'[{"page":1,"pages":1},['
            b'{"countryiso3code":"COL","date":"2023","value":20000},'
            b'{"countryiso3code":"USA","date":"2023","value":80000}]]'
        )
        spec = make_spec(
            adapter="world_bank_percent_times_level",
            direction="input",
            score_eligible=False,
            source_status="conditional",
            level_url="https://example.test/level",
            expected_latest_value={"COL": Decimal("800"), "USA": Decimal("6400")},
            minimum_observations_per_entity=1,
        )

        observations = parse_world_bank_percent_times_level(percentages, levels, spec)

        self.assertEqual([row.value for row in observations], [Decimal("800"), Decimal("6400")])
        self.assertTrue(all(row.observation_kind == "derived" for row in observations))

    def test_percent_adapter_requests_json_for_both_resources(self) -> None:
        percentages = (
            b'[{"page":1,"pages":1},['
            b'{"countryiso3code":"COL","date":"2023","value":4},'
            b'{"countryiso3code":"USA","date":"2023","value":8}]]'
        )
        levels = (
            b'[{"page":1,"pages":1},['
            b'{"countryiso3code":"COL","date":"2023","value":20000},'
            b'{"countryiso3code":"USA","date":"2023","value":80000}]]'
        )
        calls: list[tuple[str, str]] = []

        def fetcher(url: str, *, accept: str, **_kwargs: object) -> FetchedPayload:
            calls.append((url, accept))
            content = levels if url.endswith("/level") else percentages
            return FetchedPayload(url, url, content, "application/json")

        spec = make_spec(
            adapter="world_bank_percent_times_level",
            direction="input",
            score_eligible=False,
            source_status="conditional",
            level_url="https://example.test/level",
            expected_latest_value={"COL": Decimal("800"), "USA": Decimal("6400")},
            minimum_observations_per_entity=1,
        )

        observations, payloads = _acquire_series(
            spec,
            timeout=5,
            max_bytes=10_000,
            fetcher=fetcher,
        )

        self.assertEqual(len(observations), 2)
        self.assertEqual(len(payloads), 2)
        self.assertTrue(all("json" in accept for _, accept in calls))

    def test_oecd_percent_times_level_skips_explicit_missing_value(self) -> None:
        percentages = (
            b"REF_AREA,TIME_PERIOD,OBS_VALUE,UNIT_MULT,MEASURE,EXPENDITURE,OBS_STATUS\n"
            b"COL,2022,2,0,GE,GF03,A\nCOL,2023,2.5,0,GE,GF03,A\n"
            b"USA,2022,3,0,GE,GF03,A\nUSA,2023,,0,GE,GF03,A\n"
        )
        levels = (
            b'[{"page":1,"pages":1},['
            b'{"countryiso3code":"COL","date":"2022","value":20000},'
            b'{"countryiso3code":"COL","date":"2023","value":24000},'
            b'{"countryiso3code":"USA","date":"2022","value":80000},'
            b'{"countryiso3code":"USA","date":"2023","value":82000}]]'
        )
        spec = make_spec(
            adapter="oecd_percent_times_level",
            direction="input",
            score_eligible=False,
            source_status="conditional",
            level_url="https://example.test/level",
            dimension_filters={"MEASURE": "GE", "EXPENDITURE": "GF03"},
            expected_latest_year={"COL": 2023, "USA": 2022},
            expected_latest_value={"COL": Decimal("600"), "USA": Decimal("2400")},
            minimum_observations_per_entity=1,
        )

        observations = parse_oecd_percent_times_level(percentages, levels, spec)

        self.assertEqual(len(observations), 3)
        self.assertEqual(observations[-1].value, Decimal("2400"))

    def test_oecd_ratio_times_level_omits_incomplete_country_year(self) -> None:
        numerator = (
            b"REF_AREA,TIME_PERIOD,OBS_VALUE,TRANSACTION,UNIT_MULT,CURRENCY,OBS_STATUS\n"
            b"COL,2022,2,D1,6,COP,A\nCOL,2022,3,P2,6,COP,A\n"
            b"COL,2023,2,D1,6,COP,A\nCOL,2023,2,P2,6,COP,A\n"
            b"USA,2022,4,D1,6,USD,A\nUSA,2022,2,P2,6,USD,A\n"
            b"USA,2023,4,D1,6,USD,A\nUSA,2023,,P2,6,USD,A\n"
        )
        denominator = (
            b"REF_AREA,TIME_PERIOD,OBS_VALUE,UNIT_MULT,CURRENCY,OBS_STATUS\n"
            b"COL,2022,10,6,COP,A\nCOL,2023,10,6,COP,A\n"
            b"USA,2022,12,6,USD,A\nUSA,2023,12,6,USD,A\n"
        )
        levels = (
            b'[{"page":1,"pages":1},['
            b'{"countryiso3code":"COL","date":"2022","value":20000},'
            b'{"countryiso3code":"COL","date":"2023","value":22000},'
            b'{"countryiso3code":"USA","date":"2022","value":80000},'
            b'{"countryiso3code":"USA","date":"2023","value":82000}]]'
        )
        spec = make_spec(
            adapter="oecd_ratio_times_level",
            category_column="TRANSACTION",
            expected_categories=("D1", "P2"),
            direction="input",
            score_eligible=False,
            source_status="conditional",
            level_url="https://example.test/level",
            expected_latest_year={"COL": 2023, "USA": 2022},
            expected_latest_value={"COL": Decimal("8800"), "USA": Decimal("40000")},
            minimum_observations_per_entity=1,
        )

        observations = parse_oecd_ratio_times_level(numerator, denominator, levels, spec)

        self.assertEqual(len(observations), 3)
        self.assertEqual(observations[-1].value, Decimal("40000"))

    def test_accepts_different_latest_year_per_country(self) -> None:
        spec = make_spec(
            expected_latest_year={"COL": 2024, "USA": 2023},
            expected_latest_value={"COL": Decimal("1"), "USA": Decimal("1")},
            minimum_observations_per_entity=1,
        )
        rows = [
            Observation(
                entity=entity,
                period=period,
                indicator_id=spec.indicator_id,
                value=Decimal("1"),
                direction=spec.direction,
                unit=spec.unit,
                source_id=spec.source_id,
                series_code=spec.series_code,
                source_status=spec.source_status,
                score_eligible=spec.score_eligible,
                observation_status="observed",
                observation_kind="reported",
                resource_id=spec.resource_id,
            )
            for entity, period in [("COL", 2024), ("USA", 2023)]
        ]

        self.assertEqual(len(validate_observations(rows, spec)), 2)

    def test_accepts_anchor_checkpoints_for_a_larger_country_sample(self) -> None:
        spec = make_spec(
            expected_entities=("CHL", "COL", "USA"),
            expected_latest_year={"COL": 2023, "USA": 2023},
            expected_latest_value={"COL": Decimal("1"), "USA": Decimal("1")},
            minimum_observations_per_entity=1,
        )
        rows = [
            Observation(
                entity=entity,
                period=2023,
                indicator_id=spec.indicator_id,
                value=Decimal("1"),
                direction=spec.direction,
                unit=spec.unit,
                source_id=spec.source_id,
                series_code=spec.series_code,
                source_status=spec.source_status,
                score_eligible=spec.score_eligible,
                observation_status="observed",
                observation_kind="reported",
                resource_id=spec.resource_id,
            )
            for entity in spec.expected_entities
        ]

        self.assertEqual(len(validate_observations(rows, spec)), 3)

    def test_rejects_latest_value_outside_tolerance(self) -> None:
        observations = parse_world_bank_json(WB_JSON, make_spec())
        revised = [
            row
            if not (row.entity == "COL" and row.period == 2023)
            else Observation(**{**row.__dict__, "value": Decimal("99")})
            for row in observations
        ]

        with self.assertRaisesRegex(IngestionError, "último valor revisado"):
            validate_observations(revised, make_spec())

    def test_csv_serialization_is_stable(self) -> None:
        rows = parse_world_bank_json(WB_JSON, make_spec())
        self.assertEqual(observations_to_csv(rows), observations_to_csv(list(reversed(rows))))


class PipelineTests(unittest.TestCase):
    def test_publication_rolls_back_if_second_replace_fails(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            processed = root / "processed.csv"
            provenance = root / "provenance.json"
            processed.write_bytes(b"old processed")
            provenance.write_bytes(b"old provenance")
            real_replace = os.replace

            def fail_provenance(source: object, destination: object) -> None:
                if Path(destination) == provenance:
                    raise OSError("simulated publication failure")
                real_replace(source, destination)

            with patch("iee.ingestion.os.replace", side_effect=fail_provenance):
                with self.assertRaisesRegex(IngestionError, "publicación conjunta"):
                    _atomic_write_publication(
                        ((processed, b"new processed"), (provenance, b"new provenance"))
                    )

            self.assertEqual(processed.read_bytes(), b"old processed")
            self.assertEqual(provenance.read_bytes(), b"old provenance")

    def test_repository_manifest_covers_the_full_catalog(self) -> None:
        project_root = Path(__file__).parents[1]
        manifest = load_download_manifest(project_root / "config" / "downloads.toml")
        automatic = {spec.indicator_id for spec in manifest.series}
        covered = automatic | set(manifest.manual_control_ids) | set(manifest.deferred_ids)

        self.assertEqual(len(automatic), 7)
        self.assertEqual(len(manifest.manual_controls), 2)
        self.assertEqual(len(covered), 12)
        controls = {spec.indicator_id: spec for spec in manifest.manual_controls}
        pisa_usa = next(
            value for value in controls["EDU-EQ-01"].observations if value.entity == "USA"
        )
        self.assertEqual(pisa_usa.value, Decimal("102.0"))
        self.assertEqual(pisa_usa.observation_status, "source:sampling_caution")

    def test_pipeline_rejects_path_collisions_before_downloading(self) -> None:
        project_root = Path(__file__).parents[1]
        manifest_path = project_root / "config" / "downloads_inputs_v0.2.toml"
        manifest = load_download_manifest(manifest_path)
        assert manifest.country_universe is not None
        fetch_called = False

        def forbidden_fetcher(_url: str, **_kwargs: object) -> FetchedPayload:
            nonlocal fetch_called
            fetch_called = True
            raise AssertionError("fetcher must not be called")

        with TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            protected_inputs = (
                manifest_path,
                manifest.catalog_path,
                manifest.country_universe.path,
            )
            for protected in protected_inputs:
                with self.subTest(protected=protected.name):
                    with self.assertRaisesRegex(
                        IngestionError,
                        "salida no puede sobrescribir una entrada",
                    ):
                        run_pipeline(
                            manifest_path,
                            raw_dir=temporary / "raw",
                            processed_path=protected,
                            provenance_path=temporary / "provenance.json",
                            fetcher=forbidden_fetcher,
                        )
            with self.assertRaisesRegex(IngestionError, "raw_dir no puede"):
                run_pipeline(
                    manifest_path,
                    raw_dir=manifest.catalog_path,
                    processed_path=temporary / "processed.csv",
                    provenance_path=temporary / "provenance.json",
                    fetcher=forbidden_fetcher,
                )

            with self.assertRaisesRegex(IngestionError, "recurso crudo no puede"):
                _validate_raw_targets(
                    manifest_path,
                    manifest,
                    (manifest.catalog_path,),
                    (temporary / "processed.csv", temporary / "provenance.json"),
                )
        self.assertFalse(fetch_called)

    def test_pipeline_uses_fake_network_and_writes_provenance(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            catalog = root / "pilot_sources.toml"
            manifest = root / "downloads.toml"
            manual_controls = root / "manual_controls.toml"
            country_universe = root / "country_universe.toml"
            catalog.write_text(
                """
[[series]]
indicator_id = "SEG-RES-01"
source_id = "UNODC-WDI"
status = "validated"
direction = "lower"
official_code = "VC.IHR.PSRC.P5"
unit = "Víctimas por 100.000 habitantes"
exact_url = "https://example.test/data"
reference_year = 2023
latest_col_year = 2023
latest_col_value = 24.913442
latest_usa_year = 2023
latest_usa_value = 5.76340794

[[series]]
indicator_id = "ADM-RES-01"
source_id = "UN-EGDI"
status = "validated"
direction = "higher"
official_code = "OSI | Technical Appendix Table 7"
unit = "Índice de 0 a 1"
exact_url = "https://example.test/osi"
latest_col_year = 2024
latest_col_value = 0.7521
latest_col_status = "observed"
latest_usa_year = 2024
latest_usa_value = 0.9136
latest_usa_status = "observed"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            manual_controls.write_text(
                """
version = "test"
validation_date = "2026-08-23"
countries = ["COL", "USA"]

[[series]]
resource_id = "adm-res-01-control"
indicator_id = "ADM-RES-01"
source_id = "UN-EGDI"
source_status = "validated"
score_eligible = true
series_code = "OSI | Technical Appendix Table 7"
source_url = "https://example.test/osi"
release = "UN E-Government Survey 2024"
locator = "Table 7"
direction = "higher"
unit = "Índice de 0 a 1"

[[series.observations]]
entity = "COL"
period = 2024
value = 0.7521
observation_status = "observed"

[[series.observations]]
entity = "USA"
period = 2024
value = 0.9136
observation_status = "observed"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            country_universe.write_text(
                """
version = "test"
snapshot_date = "2026-08-23"
frame = "TEST-2"
official_source = "https://example.test/universe"
membership_count = 2
estimation_sample = "per-dimension"
frontier_min_countries = 2
require_complete_indicator_window = true
allow_imputation_for_eligibility = false
retain_flagged_observations = true
countries = ["COL", "USA"]

[[input_masks]]
indicator_id = "SEG-RES-01"
included_countries = ["COL", "USA"]
excluded_countries = []
""".strip()
                + "\n",
                encoding="utf-8",
            )
            manifest.write_text(
                """
version = "test"
schema_version = "iee-observations-v1"
catalog = "pilot_sources.toml"
country_universe = "country_universe.toml"
countries = ["COL", "USA"]
manual_controls = "manual_controls.toml"
deferred_ids = []

[[series]]
resource_id = "seg-res-01"
indicator_id = "SEG-RES-01"
source_id = "UNODC-WDI"
source_status = "validated"
score_eligible = true
adapter = "world_bank_json"
series_code = "VC.IHR.PSRC.P5"
url = "https://example.test/data"
direction = "lower"
unit = "Víctimas por 100.000 habitantes"
expected_entities = ["COL", "USA"]
expected_latest_year = { COL = 2023, USA = 2023 }
expected_latest_value = { COL = 24.913442, USA = 5.76340794 }
latest_value_tolerance = 0.000001
minimum_observations_per_entity = 2
reference_year = 2023
""".strip()
                + "\n",
                encoding="utf-8",
            )

            original_manual_bytes = manual_controls.read_bytes()

            def fetcher(url: str, **_kwargs: object) -> FetchedPayload:
                manual_controls.write_bytes(
                    original_manual_bytes + b"\n# cambio concurrente posterior a la carga\n"
                )
                return FetchedPayload(url, url, WB_JSON, "application/json")

            processed = root / "processed" / "observations.csv"
            provenance = root / "interim" / "provenance.json"
            with patch.object(
                socket,
                "create_connection",
                side_effect=AssertionError("network disabled in tests"),
            ):
                result = run_pipeline(
                    manifest,
                    raw_dir=root / "raw",
                    processed_path=processed,
                    provenance_path=provenance,
                    fetcher=fetcher,
                    retrieved_at="2026-08-23T12:00:00+00:00",
                )

            self.assertEqual(result.observation_count, 6)
            self.assertEqual(result.series_count, 2)
            self.assertEqual(result.raw_resource_count, 1)
            self.assertTrue(processed.exists())
            self.assertTrue(provenance.exists())
            self.assertEqual(len(list((root / "raw").glob("*.json"))), 1)
            self.assertIn("manual_control", processed.read_text(encoding="utf-8"))
            receipt = json.loads(provenance.read_text(encoding="utf-8"))
            self.assertEqual(receipt["series_counts"]["manual_control"], 1)
            self.assertEqual(receipt["manual_controls"]["indicator_ids"], ["ADM-RES-01"])
            self.assertEqual(receipt["manual_controls"]["validation_date"], "2026-08-23")
            self.assertEqual(
                receipt["manual_controls"]["sha256"], sha256_hex(original_manual_bytes)
            )
            self.assertNotEqual(
                receipt["manual_controls"]["sha256"],
                sha256_hex(manual_controls.read_bytes()),
            )
            self.assertEqual(receipt["country_universe"]["frame"], "TEST-2")
            self.assertEqual(receipt["country_universe"]["membership_count"], 2)
            automatic = next(
                row for row in receipt["series"] if row["indicator_id"] == "SEG-RES-01"
            )
            self.assertEqual(automatic["country_mask"]["included_count"], 2)
            self.assertTrue(automatic["country_mask"]["frontier_min_met"])
            self.assertEqual(automatic["vintage_age"], {"COL": 0, "USA": 0})

            manual_controls.write_bytes(
                original_manual_bytes.replace(
                    b'direction = "higher"', b'direction = "lower"'
                )
            )
            with self.assertRaisesRegex(IngestionError, "direction difiere"):
                load_download_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
