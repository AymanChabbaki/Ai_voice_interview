import os
import sys
import types
from importlib import import_module

import pytest


def _install_lightweight_ml_stubs():
    # Stub sentence_transformers.SentenceTransformer used during app import/startup.
    sentence_transformers_module = types.ModuleType("sentence_transformers")

    class DummySentenceTransformer:
        def __init__(self, *args, **kwargs):
            pass

    sentence_transformers_module.SentenceTransformer = DummySentenceTransformer
    sys.modules["sentence_transformers"] = sentence_transformers_module

    # Stub sklearn.metrics.pairwise.cosine_similarity imported by app.py.
    sklearn_module = types.ModuleType("sklearn")
    sklearn_metrics_module = types.ModuleType("sklearn.metrics")
    sklearn_pairwise_module = types.ModuleType("sklearn.metrics.pairwise")

    def cosine_similarity(*args, **kwargs):
        return [[1.0]]

    sklearn_pairwise_module.cosine_similarity = cosine_similarity

    sys.modules["sklearn"] = sklearn_module
    sys.modules["sklearn.metrics"] = sklearn_metrics_module
    sys.modules["sklearn.metrics.pairwise"] = sklearn_pairwise_module


@pytest.fixture(scope="session")
def app_module():
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")
    _install_lightweight_ml_stubs()
    return import_module("app")
