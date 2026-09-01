import json
import subprocess
from pathlib import Path
from unittest import mock

from spotticus.models import DataConfidence, ProbeStatus
from spotticus.probes.codexbar import CodexBarProbe, parse_codexbar_json

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "codexbar_claude.json"


def test_parse_codexbar_json_success():
    with open(FIXTURE_PATH) as f:
        json_str = f.read()

    report = parse_codexbar_json(json_str)
    assert report.status == ProbeStatus.OK
    assert len(report.results) == 1
    
    res = report.results[0]
    assert res.provider == "claude"
    assert res.status == ProbeStatus.OK
    assert res.data_confidence == DataConfidence.PERCENT_ONLY
    assert len(res.pools["default"]) == 2
    
    primary = next(w for w in res.pools["default"] if w.name == "primary")
    assert primary.window_minutes == 300
    assert primary.is_session
    assert not primary.is_weekly
    assert primary.used_percent == 0.0
    
    secondary = next(w for w in res.pools["default"] if w.name == "secondary")
    assert secondary.window_minutes == 10080
    assert not secondary.is_session
    assert secondary.is_weekly
    assert secondary.used_percent == 38.0


def test_parse_codexbar_json_missing_usage():
    data = [{"provider": "bad_provider"}]
    report = parse_codexbar_json(json.dumps(data))
    assert report.status == ProbeStatus.OK
    assert len(report.results) == 1
    assert report.results[0].status == ProbeStatus.FAILED
    assert "Missing usage dict" in report.results[0].error


def test_parse_codexbar_json_malformed():
    report = parse_codexbar_json("{ bad json")
    assert report.status == ProbeStatus.FAILED


def test_parse_codexbar_json_not_array():
    report = parse_codexbar_json('{"provider": "claude"}')
    assert report.status == ProbeStatus.FAILED


def test_codexbar_probe_subprocess_timeout():
    probe = CodexBarProbe()
    with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="codexbar", timeout=10)):
        report = probe.probe()
    assert report.status == ProbeStatus.FAILED
    assert report.error == "TimeoutExpired"


def test_codexbar_probe_subprocess_nonzero_exit():
    probe = CodexBarProbe()
    err = subprocess.CalledProcessError(returncode=1, cmd="codexbar", stderr="boom")
    with mock.patch("subprocess.run", side_effect=err):
        report = probe.probe()
    assert report.status == ProbeStatus.FAILED
    assert "boom" in report.error


def test_codexbar_probe_missing_from_path():
    probe = CodexBarProbe()
    with mock.patch("subprocess.run", side_effect=FileNotFoundError):
        report = probe.probe()
    assert report.status == ProbeStatus.FAILED
    assert "not on PATH" in report.error

def test_parse_codexbar_antigravity():
    path = Path(__file__).parent / "fixtures" / "codexbar_antigravity.json"
    with open(path) as f:
        json_str = f.read()
    
    report = parse_codexbar_json(json_str)
    assert report.status == ProbeStatus.OK
    res = report.results[0]
    assert "gemini" in res.pools
    assert len(res.pools["gemini"]) == 2
    assert "claude" in res.pools
    assert len(res.pools["claude"]) == 2

def test_parse_codexbar_cursor():
    path = Path(__file__).parent / "fixtures" / "codexbar_cursor.json"
    with open(path) as f:
        json_str = f.read()
    
    report = parse_codexbar_json(json_str)
    assert report.status == ProbeStatus.OK
    res = report.results[0]
    assert "premium" in res.pools
    assert len(res.pools["premium"]) == 2
    assert "cursor-models" in res.pools
    assert len(res.pools["cursor-models"]) == 1
    assert "grok" in res.pools
    assert len(res.pools["grok"]) == 1
