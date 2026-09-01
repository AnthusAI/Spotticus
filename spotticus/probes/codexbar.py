import json
import subprocess
from datetime import datetime

from spotticus.models import DataConfidence, ProbeReport, ProbeResult, ProbeStatus, WindowUsage
from spotticus.probes import LeftoverProbe


def parse_codexbar_json(json_str: str) -> ProbeReport:
    """Parse CodexBar JSON output into a ProbeReport with multiple ProbeResults."""
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return ProbeReport(status=ProbeStatus.FAILED, error=f"Malformed JSON: {e}")

    if not isinstance(data, list):
        return ProbeReport(status=ProbeStatus.FAILED, error="Expected JSON array at root")

    results = []
    for item in data:
        provider = item.get("provider", "unknown")
        
        # If there's no usage dict, this provider's data is incomplete
        usage_data = item.get("usage")
        if not isinstance(usage_data, dict):
            results.append(
                ProbeResult(
                    provider=provider,
                    status=ProbeStatus.FAILED,
                    data_confidence=DataConfidence.UNKNOWN,
                    error="Missing usage dict",
                )
            )
            continue

        try:
            conf_str = usage_data.get("dataConfidence", "unknown")
            data_confidence = DataConfidence(conf_str)
        except ValueError:
            data_confidence = DataConfidence.UNKNOWN

        updated_at_str = usage_data.get("updatedAt")
        updated_at = None
        if updated_at_str:
            try:
                # Handle Z timezone suffix
                updated_at_str = updated_at_str.replace("Z", "+00:00")
                updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                pass

        windows = []
        # Check standard window keys: primary, secondary, tertiary
        for key in ["primary", "secondary", "tertiary"]:
            win_data = usage_data.get(key)
            if not isinstance(win_data, dict):
                continue
                
            try:
                used_percent = float(win_data["usedPercent"])
                window_minutes = int(win_data["windowMinutes"])
                resets_at_str = win_data["resetsAt"].replace("Z", "+00:00")
                resets_at = datetime.fromisoformat(resets_at_str)
                reset_description = win_data.get("resetDescription", "")
                
                # Determine window type based on minutes (heuristics from manager)
                is_session = (window_minutes == 300)
                is_weekly = (window_minutes == 10080)
                
                windows.append(
                    WindowUsage(
                        name=key,
                        is_session=is_session,
                        is_weekly=is_weekly,
                        used_percent=used_percent,
                        window_minutes=window_minutes,
                        resets_at=resets_at,
                        reset_description=reset_description,
                    )
                )
            except (KeyError, ValueError, TypeError) as e:
                # If a window is malformed, we could fail the provider. Let's just fail it.
                windows = []
                results.append(
                    ProbeResult(
                        provider=provider,
                        status=ProbeStatus.FAILED,
                        data_confidence=data_confidence,
                        error=f"Malformed window '{key}': {e}",
                    )
                )
                break
        
        # If we broke out of the loop and added a failed result, windows will be empty.
        # But if windows is empty because there are just no windows, we shouldn't skip the else block
        # Actually, let's just use a flag or check if the last result was this provider.
        if results and results[-1].provider == provider and results[-1].status == ProbeStatus.FAILED:
            continue
            
        results.append(
            ProbeResult(
                provider=provider,
                status=ProbeStatus.OK,
                data_confidence=data_confidence,
                windows=windows,
                source=item.get("source"),
                updated_at=updated_at,
            )
        )

    return ProbeReport(status=ProbeStatus.OK, results=results)


class CodexBarProbe(LeftoverProbe):
    """Probe that calls the local codexbar CLI."""

    def probe(self) -> ProbeReport:
        try:
            process = subprocess.run(
                ["codexbar", "usage", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            return parse_codexbar_json(process.stdout)
        except subprocess.TimeoutExpired:
            return ProbeReport(status=ProbeStatus.FAILED, error="TimeoutExpired")
        except subprocess.CalledProcessError as e:
            return ProbeReport(status=ProbeStatus.FAILED, error=f"Non-zero exit: {e.stderr}")
        except FileNotFoundError:
            return ProbeReport(status=ProbeStatus.FAILED, error="codexbar not on PATH")
        except Exception as e:
            return ProbeReport(status=ProbeStatus.FAILED, error=str(e))
