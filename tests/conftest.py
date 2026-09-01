import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_locks_dir(tmp_path):
    with patch("spotticus.locks.get_locks_dir", return_value=tmp_path):
        yield tmp_path
