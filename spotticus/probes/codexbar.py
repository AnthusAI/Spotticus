import json
import subprocess
from datetime import datetime

from spotticus.models import DataConfidence, ProbeReport, ProbeResult, ProbeStatus, WindowUsage
from spotticus.probes import LeftoverProbe


def _parse_window(key: str, win_data: dict) -> WindowUsage | None:
    try:
        used_percent = float(win_data["usedPercent"])
        window_minutes = int(win_data["windowMinutes"])
        resets_at_str = win_data["resetsAt"].replace("Z", "+00:00")
        resets_at = datetime.fromisoformat(resets_at_str)
        reset_description = win_data.get("resetDescription", "")
        
        is_session = (window_minutes == 300)
        is_weekly = (window_minutes == 10080)
        
        return WindowUsage(
            name=key,
            is_session=is_session,
            is_weekly=is_weekly,
            used_percent=used_percent,
            window_minutes=window_minutes,
            resets_at=resets_at,
            reset_description=reset_description,
        )
    except (KeyError, ValueError, TypeError):
        return None


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
                updated_at_str = updated_at_str.replace("Z", "+00:00")
                updated_at = datetime.fromisoformat(updated_at_str)
            except ValueError:
                pass

        pools: dict[str, list[WindowUsage]] = {}
        error = None

        if provider == "antigravity":
            extra_windows = usage_data.get("extraRateWindows", [])
            for win_wrapper in extra_windows:
                if not isinstance(win_wrapper, dict):
                    continue
                win_id = win_wrapper.get("id", "unknown")
                win_data = win_wrapper.get("window")
                if not isinstance(win_data, dict):
                    continue
                parsed_win = _parse_window(win_id, win_data)
                if not parsed_win:
                    error = f"Malformed window in extraRateWindows: '{win_id}'"
                    break
                
                if "gemini" in win_id:
                    pools.setdefault("gemini", []).append(parsed_win)
                elif "3p" in win_id:
                    pools.setdefault("claude", []).append(parsed_win)
                else:
                    pools.setdefault("default", []).append(parsed_win)
        
        elif provider == "cursor":
            for key in ["primary", "secondary", "tertiary"]:
                win_data = usage_data.get(key)
                if not isinstance(win_data, dict):
                    continue
                parsed_win = _parse_window(key, win_data)
                if not parsed_win:
                    error = f"Malformed window '{key}'"
                    break
                
                if key in ("primary", "secondary"):
                    pools.setdefault("premium", []).append(parsed_win)
                elif key == "tertiary":
                    pools.setdefault("cursor-models", []).append(parsed_win)
                else:
                    pools.setdefault("default", []).append(parsed_win)
            
            # Parse extraRateWindows for grok bot
            extra_windows = usage_data.get("extraRateWindows", [])
            for win_wrapper in extra_windows:
                if not isinstance(win_wrapper, dict):
                    continue
                win_id = win_wrapper.get("id", "unknown")
                if win_id == "cursor-grok-bot":
                    win_data = win_wrapper.get("window")
                    if isinstance(win_data, dict):
                        parsed_win = _parse_window(win_id, win_data)
                        if parsed_win:
                            pools.setdefault("grok", []).append(parsed_win)
        
        else:
            # Default for claude, codex, etc.
            for key in ["primary", "secondary", "tertiary"]:
                win_data = usage_data.get(key)
                if not isinstance(win_data, dict):
                    continue
                parsed_win = _parse_window(key, win_data)
                if not parsed_win:
                    error = f"Malformed window '{key}'"
                    break
                pools.setdefault("default", []).append(parsed_win)

        if error:
            results.append(
                ProbeResult(
                    provider=provider,
                    status=ProbeStatus.FAILED,
                    data_confidence=data_confidence,
                    error=error,
                )
            )
            continue
            
        results.append(
            ProbeResult(
                provider=provider,
                status=ProbeStatus.OK,
                data_confidence=data_confidence,
                pools=pools,
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
                timeout=60,
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
