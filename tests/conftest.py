"""Test configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Get test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {
            "text": "Python is a high-level programming language.",
            "metadata": {"source": "test"},
        },
        {
            "text": "Machine learning is a subset of artificial intelligence.",
            "metadata": {"source": "test"},
        },
    ]
