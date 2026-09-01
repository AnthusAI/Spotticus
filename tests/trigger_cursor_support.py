"""Harness for running scripts/trigger_cursor.sh against stub binaries."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "trigger_cursor.sh"
SKILL_PATH = REPO_ROOT / "skills" / "composer-spot-worker.md"
HOST_CAT = shutil.which("cat") or "/bin/cat"
HOST_GREP = shutil.which("grep") or "/usr/bin/grep"
HOST_DIRNAME = shutil.which("dirname") or "/usr/bin/dirname"
HOST_PYTHON = shutil.which("python3") or "/usr/bin/python3"


def write_executable(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def _install_host_tool_shims(bin_dir: Path) -> None:
    write_executable(bin_dir / "cat", f'#!/bin/bash\nexec "{HOST_CAT}" "$@"\n')
    write_executable(bin_dir / "grep", f'#!/bin/bash\nexec "{HOST_GREP}" "$@"\n')
    write_executable(bin_dir / "dirname", f'#!/bin/bash\nexec "{HOST_DIRNAME}" "$@"\n')
    write_executable(bin_dir / "python3", f'#!/bin/bash\nexec "{HOST_PYTHON}" "$@"\n')


def install_fake_spotticus(bin_dir: Path, log_path: Path, eligible: bool) -> Path:
    eligible_json = json.dumps(
        {
            "providers": [
                {
                    "provider": "cursor",
                    "is_eligible": eligible,
                    "pools": {"cursor-models": {"is_eligible": eligible}},
                }
            ]
        }
    )
    script = bin_dir / "spotticus"
    write_executable(
        script,
        f"""#!/bin/bash
echo "$@" >> "{log_path}"
cmd="$1"
shift
case "$cmd" in
  status)
    echo '{eligible_json}'
    if [ "{int(eligible)}" = "1" ]; then
      exit 0
    fi
    exit 1
    ;;
  claim)
    echo "Lock claimed for target $1."
    exit 0
    ;;
  release)
    echo "Lock released for target $1."
    exit 0
    ;;
  *)
    echo "unexpected spotticus command: $cmd" >&2
    exit 2
    ;;
esac
""",
    )
    return script


def install_fake_agent(bin_dir: Path, argv_path: Path) -> Path:
    script = bin_dir / "agent"
    write_executable(
        script,
        f"""#!/bin/bash
python3 -c 'import json, sys; json.dump(sys.argv[2:], open(sys.argv[1], "w"))' "{argv_path}" "$@"
exit 0
""",
    )
    return script


def composer_invocation_ok(argv: list[str], repo_root: str | Path) -> None:
    assert "-p" in argv, argv
    assert "--model" in argv, argv
    assert "composer-2.5" in argv, argv
    assert "--trust" in argv, argv
    assert "--force" in argv, argv
    prompt = argv[argv.index("-p") + 1]
    assert "composer-spot-worker" in prompt, prompt
    assert "spot:cursor" in prompt, prompt
    assert "--workspace" in argv, argv
    assert argv[argv.index("--workspace") + 1] == str(repo_root), argv


def run_trigger_cursor(
    tmp_path: Path,
    *,
    eligible: bool,
    agent_on_path: bool,
) -> SimpleNamespace:
    bin_dir = tmp_path / "bin"
    log_path = tmp_path / "spotticus.log"
    argv_path = tmp_path / "agent.argv"
    _install_host_tool_shims(bin_dir)
    spotticus = install_fake_spotticus(bin_dir, log_path, eligible=eligible)
    if agent_on_path:
        install_fake_agent(bin_dir, argv_path)

    env = os.environ.copy()
    env["SPOTTICUS_CMD"] = str(spotticus)
    env["PATH"] = str(bin_dir)

    result = subprocess.run(
        ["/bin/bash", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
    )
    return SimpleNamespace(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        spotticus_log=log_path.read_text() if log_path.exists() else "",
        agent_argv=argv_path.read_text() if argv_path.exists() else "",
    )


def claimed_target(log: str, target: str) -> bool:
    return any(line.split()[:2] == ["claim", target] for line in log.splitlines())


def released_target(log: str, target: str) -> bool:
    return any(line.split()[:2] == ["release", target] for line in log.splitlines())
