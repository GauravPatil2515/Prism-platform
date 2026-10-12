import os
import pytest
from fastapi.testclient import TestClient

from web import app as app_mod
from web import security


def test_clear_scans_purges_residual_reports(monkeypatch, tmp_path):
    results_dir = tmp_path / "results"
    scans_dir = tmp_path / "scan_data"
    results_dir.mkdir()
    scans_dir.mkdir()

    monkeypatch.setattr(app_mod, "_RESULTS_DIR", str(results_dir))
    monkeypatch.setattr(app_mod, "_SCANS_DIR", str(scans_dir))
    monkeypatch.setattr(security, "_API_KEYS", ["test-key"])

    # Create dummy report files in results_dir
    html_report = results_dir / "report_example.com_20261012_120000.html"
    pdf_report = results_dir / "report_example.com_20261012_120000.pdf"
    other_file = results_dir / "keep_me.txt"

    html_report.write_text("<html></html>")
    pdf_report.write_bytes(b"%PDF-1.4")
    other_file.write_text("keep")

    client = TestClient(app_mod.app, raise_server_exceptions=True)
    resp = client.delete("/api/scans", headers={"X-API-Key": "test-key"})
    assert resp.status_code == 200

    # Report files should be deleted
    assert not html_report.exists()
    assert not pdf_report.exists()
    # Non-report file should be untouched
    assert other_file.exists()
