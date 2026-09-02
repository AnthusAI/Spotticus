import json
import os
import signal
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore


class LockState(Enum):
    CLAIMED = "CLAIMED"
    HELD = "HELD"


@dataclass
class LockData:
    target: str
    product: str
    model: str
    name: str
    pid: int
    state: LockState
    timestamp: float
    session_id: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["state"] = self.state.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "LockData":
        d = d.copy()
        d["state"] = LockState(d["state"])
        return cls(**d)


def get_locks_dir() -> Path:
    # Use ~/.spotticus/locks as per requirement
    path = Path.home() / ".spotticus" / "locks"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_lock_path(target: str) -> Path:
    return get_locks_dir() / f"{target}.json"


def _is_process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # If we don't have permission to signal the process, it exists.
        return True
    except OSError:
        return False


def _load_lock_data(f) -> Optional[LockData]:
    try:
        content = f.read()
        if not content:
            return None
        data = json.loads(content)
        lock_data = LockData.from_dict(data)
        
        # Stale lock handling
        if lock_data.state == LockState.CLAIMED:
            if not _is_process_alive(lock_data.pid):
                return None  # Treat as stale
        return lock_data
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


@contextmanager
def acquire_provider_lock(target: str):
    """
    Acquire a file lock on the provider's lockfile, yielding the file object.
    Creates the file if it doesn't exist.
    """
    path = get_lock_path(target)
    
    # We use open with "a+" to avoid truncating if it exists,
    # and then seek(0) to read it.
    with open(path, "a+") as f:
        if fcntl:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.seek(0)
            yield f
        finally:
            if fcntl:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def read_lock(target: str) -> Optional[LockData]:
    """Read the current valid lock for a provider. Stale locks are ignored (treated as None).

    Reading a lock must not create one. acquire_provider_lock opens with "a+", which would
    leave an empty lockfile behind for every pool a probe merely inspects - and an empty
    file is enough to trip a "no lock remains" assertion (and to litter ~/.spotticus/locks).
    """
    path = get_lock_path(target)
    if not path.exists():
        return None
    with acquire_provider_lock(target) as f:
        return _load_lock_data(f)


def claim_lock(target: str, product: str, model: str, name: str, pid: int, session_id: Optional[str] = None) -> bool:
    """
    Attempt to claim the lock. Returns True if successful, False if already locked.
    Automatically cleans up or overwrites stale locks.
    """
    with acquire_provider_lock(target) as f:
        current_lock = _load_lock_data(f)
        if current_lock is not None:
            return False  # Already held or actively claimed
        
        # Create new lock
        new_lock = LockData(
            target=target,
            product=product,
            model=model,
            name=name,
            pid=pid,
            state=LockState.CLAIMED,
            timestamp=time.time(),
            session_id=session_id
        )
        f.seek(0)
        f.truncate(0)
        json.dump(new_lock.to_dict(), f)
        return True


def release_lock(target: str, pid: int) -> tuple[bool, str]:
    """
    Release a claim lock if the pid matches. HELD locks are ignored.
    Returns (True, "") if successfully released, or (False, "reason") if failed.
    """
    with acquire_provider_lock(target) as f:
        current_lock = _load_lock_data(f)
        if current_lock is None:
            return True, ""  # Already unlocked
            
        if current_lock.state == LockState.HELD:
            return False, "Cannot release a HELD lock. Use 'spotticus unhold' instead."
            
        if current_lock.pid != pid:
            return False, f"PID mismatch. Expected {current_lock.pid}, got {pid}."
            
        # Clear the lockfile
        f.seek(0)
        f.truncate(0)
        
        # We can actually just remove the file to clean up
        try:
            get_lock_path(target).unlink(missing_ok=True)
        except OSError:
            pass
        return True, ""


def unhold_lock(target: str) -> None:
    """
    Unconditionally removes the lockfile if it exists, regardless of its state.
    """
    with acquire_provider_lock(target) as f:
        # Clear the lockfile
        f.seek(0)
        f.truncate(0)
        try:
            get_lock_path(target).unlink(missing_ok=True)
        except OSError:
            pass


def hold_lock(target: str) -> None:
    """
    Preempts the current lock (if CLAIMED) by sending SIGTERM to its pid,
    and sets the lock state to HELD.
    """
    with acquire_provider_lock(target) as f:
        current_lock = _load_lock_data(f)
        
        if current_lock is not None and current_lock.state == LockState.CLAIMED:
            # Send SIGTERM
            try:
                os.kill(current_lock.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
                
        # Write HELD lock
        held_lock = LockData(
            target=target,
            product=current_lock.product if current_lock else "n/a",
            model=current_lock.model if current_lock else "n/a",
            name=current_lock.name if current_lock else "n/a",
            pid=-1,
            state=LockState.HELD,
            timestamp=time.time(),
            session_id=current_lock.session_id if current_lock else None
        )
        f.seek(0)
        f.truncate(0)
        json.dump(held_lock.to_dict(), f)
