import json
import os
import signal
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from spotticus.locks import (
    LockData,
    LockState,
    claim_lock,
    get_lock_path,
    get_locks_dir,
    hold_lock,
    read_lock,
    release_lock,
)

@pytest.fixture
def mock_locks_dir(tmp_path):
    with patch("spotticus.locks.get_locks_dir", return_value=tmp_path):
        yield tmp_path

@pytest.fixture
def mock_is_alive():
    with patch("spotticus.locks._is_process_alive", return_value=True) as mock_alive:
        yield mock_alive

def test_claim_lock_success(mock_locks_dir, mock_is_alive):
    success = claim_lock("providerA", "prod", "mod", "bot1", 1234)
    assert success is True

    # verify lock file created
    path = get_lock_path("providerA")
    assert path.exists()

    with open(path) as f:
        data = json.load(f)
    assert data["target"] == "providerA"
    assert data["state"] == LockState.CLAIMED.value
    assert data["pid"] == 1234

def test_claim_lock_already_locked(mock_locks_dir, mock_is_alive):
    assert claim_lock("providerB", "prod", "mod", "bot1", 1234) is True
    assert claim_lock("providerB", "prod", "mod", "bot2", 5678) is False

def test_claim_lock_stale(mock_locks_dir, mock_is_alive):
    assert claim_lock("providerC", "prod", "mod", "bot1", 1234) is True
    
    # simulate process 1234 dying, but 5678 is alive
    mock_is_alive.side_effect = lambda pid: pid != 1234
    
    # second claim should succeed because lock is stale
    assert claim_lock("providerC", "prod", "mod", "bot2", 5678) is True
    
    lock = read_lock("providerC")
    assert lock is not None
    assert lock.pid == 5678

def test_release_lock_success(mock_locks_dir, mock_is_alive):
    claim_lock("providerD", "prod", "mod", "bot1", 1234)
    success, reason = release_lock("providerD", 1234)
    assert success is True
    assert read_lock("providerD") is None

def test_release_lock_wrong_pid(mock_locks_dir, mock_is_alive):
    claim_lock("providerE", "prod", "mod", "bot1", 1234)
    success, reason = release_lock("providerE", 5678)
    assert success is False
    assert "PID mismatch" in reason
    assert read_lock("providerE") is not None

def test_hold_lock(mock_locks_dir, mock_is_alive):
    claim_lock("providerF", "prod", "mod", "bot1", 1234)
    
    with patch("os.kill") as mock_kill:
        hold_lock("providerF")
        mock_kill.assert_called_once_with(1234, signal.SIGTERM)
    
    lock = read_lock("providerF")
    assert lock.state == LockState.HELD

def test_hold_lock_no_process(mock_locks_dir, mock_is_alive):
    with patch("os.kill") as mock_kill:
        hold_lock("providerG")
        mock_kill.assert_not_called()
        
    lock = read_lock("providerG")
    assert lock.state == LockState.HELD

def test_release_held_lock(mock_locks_dir, mock_is_alive):
    hold_lock("providerH")
    success, reason = release_lock("providerH", -1)
    assert success is False
    assert "HELD lock" in reason

def test_unhold_lock(mock_locks_dir, mock_is_alive):
    hold_lock("providerI")
    assert read_lock("providerI").state == LockState.HELD
    
    from spotticus.locks import unhold_lock
    unhold_lock("providerI")
    assert read_lock("providerI") is None
