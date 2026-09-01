import json
from unittest import mock
import pytest

from spotticus.cli import main
from spotticus.models import ProbeReport, ProbeResult, ProbeStatus, DataConfidence, WindowUsage
from datetime import datetime, timezone, timedelta


def make_report(is_eligible=True):
    now = datetime.now(timezone.utc)
    if is_eligible:
        used = 10.0
        elapsed = 5040
    else:
        used = 50.0
        elapsed = 5040
        
    resets_at = now + timedelta(minutes=(10080 - elapsed))
    
    w = WindowUsage(
        name="primary",
        is_session=False,
        is_weekly=True,
        used_percent=used,
        window_minutes=10080,
        resets_at=resets_at,
        reset_description="",
    )
    
    result = ProbeResult(
        provider="claude",
        status=ProbeStatus.OK,
        data_confidence=DataConfidence.EXACT,
        windows=[w],
    )
    
    return ProbeReport(status=ProbeStatus.OK, results=[result])


@mock.patch("spotticus.cli.CodexBarProbe")
def test_status_human_output_eligible(mock_probe_cls, capsys):
    mock_probe = mock_probe_cls.return_value
    mock_probe.probe.return_value = make_report(is_eligible=True)
    
    exit_code = main(["status"])
    
    assert exit_code == 0
    out, err = capsys.readouterr()
    assert "🟢 ELIGIBLE" in out
    assert "CLAUDE" in out


@mock.patch("spotticus.cli.CodexBarProbe")
def test_status_human_output_ineligible(mock_probe_cls, capsys):
    mock_probe = mock_probe_cls.return_value
    mock_probe.probe.return_value = make_report(is_eligible=False)
    
    exit_code = main(["status"])
    
    assert exit_code == 1
    out, err = capsys.readouterr()
    assert "🔴 SKIP" in out


@mock.patch("spotticus.cli.CodexBarProbe")
def test_status_json_output(mock_probe_cls, capsys):
    mock_probe = mock_probe_cls.return_value
    mock_probe.probe.return_value = make_report(is_eligible=True)
    
    exit_code = main(["status", "--json"])
    
    assert exit_code == 0
    out, err = capsys.readouterr()
    data = json.loads(out)
    assert len(data["providers"]) == 1
    assert data["providers"][0]["provider"] == "claude"
    assert data["providers"][0]["is_eligible"] is True


def test_cli_no_subcommand(capsys):
    exit_code = main([])
    assert exit_code == 0
    out, err = capsys.readouterr()
    assert "Spotticus is pre-1.0. Try: spotticus status" in err
