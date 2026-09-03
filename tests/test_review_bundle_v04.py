import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.review_bundle import ReviewBundleError, run_review_bundle


class ReviewBundleV04Tests(unittest.TestCase):
    def test_hashes_review_artifacts_without_recording_an_approval(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_fixture(root)

            result = run_review_bundle(
                config,
                output_path=root / "bundle.json",
                calculated_at="2026-09-03T12:00:00+00:00",
            )

            self.assertEqual(len(result["artifacts"]), 6)
            self.assertFalse(result["review"]["approval_recorded"])
            self.assertIsNone(result["aggregate"]["ranking"])
            bundle = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
            self.assertEqual(bundle["status"], "review-ready-not-approved")

    def test_rejects_an_empty_artifact_before_writing(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_fixture(root, empty=True)

            with self.assertRaisesRegex(ReviewBundleError, "vacío"):
                run_review_bundle(config, output_path=root / "bundle.json")
            self.assertFalse((root / "bundle.json").exists())

    def _write_fixture(self, root: Path, empty: bool = False) -> Path:
        artifacts = []
        for number in range(6):
            path = root / f"artifact-{number}.md"
            path.write_text("" if empty and number == 5 else f"# Artifact {number}\n", encoding="utf-8")
            artifacts.append(
                f'''[[artifacts]]
id = "artifact_{number}"
label = "Artifact {number}"
path = "{path.name}"
'''
            )
        config = root / "bundle.toml"
        config.write_text(
            '''version = "0.4"
schema_version = "iee-review-bundle-v1"
status = "review-ready-not-approved"

'''
            + "\n".join(artifacts),
            encoding="utf-8",
        )
        return config
