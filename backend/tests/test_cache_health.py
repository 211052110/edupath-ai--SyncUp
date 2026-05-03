"""
Tests: Cache layer + Health endpoint + Train script data generators
"""

import pytest
import numpy as np


# ── Cache layer ───────────────────────────────────────────────────────────────

class TestMemoryCache:
    def test_get_miss_returns_none(self):
        from app.core.cache import _MemoryCache
        c = _MemoryCache()
        assert c.get("nonexistent") is None

    def test_set_and_get(self):
        from app.core.cache import _MemoryCache
        c = _MemoryCache()
        c.set("key1", "value1", ttl=60)
        assert c.get("key1") == "value1"

    def test_expired_returns_none(self):
        from app.core.cache import _MemoryCache
        import time
        c = _MemoryCache()
        c.set("key2", "value2", ttl=0)   # TTL=0 → already expired
        time.sleep(0.01)
        assert c.get("key2") is None

    def test_delete(self):
        from app.core.cache import _MemoryCache
        c = _MemoryCache()
        c.set("key3", "val", ttl=60)
        c.delete("key3")
        assert c.get("key3") is None

    def test_info_returns_dict(self):
        from app.core.cache import _MemoryCache
        c = _MemoryCache()
        info = c.info()
        assert "backend" in info
        assert info["backend"] == "memory"


class TestCachePublicAPI:
    def test_cache_key_deterministic(self):
        from app.core.cache import _cache_key
        k1 = _cache_key("loan", {"gpa": 3.5, "country": "USA"})
        k2 = _cache_key("loan", {"country": "USA", "gpa": 3.5})
        assert k1 == k2  # sorted keys → same hash

    def test_cache_key_namespace_isolates(self):
        from app.core.cache import _cache_key
        k1 = _cache_key("loan", {"x": 1})
        k2 = _cache_key("roi",  {"x": 1})
        assert k1 != k2

    def test_cache_get_miss(self):
        # conftest patches cache_get to always miss
        from app.core.cache import cache_get
        assert cache_get("loan", {"test": True}) is None

    def test_cache_set_noop(self):
        # conftest patches cache_set — should not raise
        from app.core.cache import cache_set
        cache_set("loan", {"test": True}, {"score": 75}, 3600)

    def test_cache_info_returns_dict(self):
        from app.core.cache import cache_info
        info = cache_info()
        assert isinstance(info, dict)


# ── Health endpoint ───────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_status_ok(self, client):
        data = client.get("/health").json()
        assert data["status"] == "ok"

    def test_health_has_cache(self, client):
        data = client.get("/health").json()
        assert "cache" in data

    def test_cache_info_endpoint(self, client):
        r = client.get("/api/v1/cache/info")
        assert r.status_code == 200
        assert "backend" in r.json()


# ── Train script: data generators ────────────────────────────────────────────

class TestDataGenerators:
    def test_loan_data_shape(self):
        from scripts.train_models import _gen_loan_data
        X, y = _gen_loan_data(n=200)
        assert X.shape[1] == 7
        assert len(y) == len(X)

    def test_loan_labels_multiclass(self):
        from scripts.train_models import _gen_loan_data
        _, y = _gen_loan_data(n=500)
        assert set(np.unique(y)).issubset({0, 1, 2})
        assert len(np.unique(y)) == 3   # all classes present

    def test_loan_features_clipped(self):
        from scripts.train_models import _gen_loan_data
        X, _ = _gen_loan_data(n=200)
        assert np.all(X[:, :4] >= 0)
        assert np.all(X[:, :4] <= 100)

    def test_roi_data_shape(self):
        from scripts.train_models import _gen_roi_data
        X, y = _gen_roi_data(n=200)
        assert X.shape[1] == 7
        assert len(y) == 200

    def test_roi_salary_in_range(self):
        from scripts.train_models import _gen_roi_data
        _, y = _gen_roi_data(n=200)
        assert np.all(y >= 30000)
        assert np.all(y <= 250000)

    def test_roi_salary_varies_by_country(self):
        """USA salaries should be higher than Germany on average."""
        from scripts.train_models import _gen_roi_data, SALARY_BY_COUNTRY_FIELD
        usa_sal = SALARY_BY_COUNTRY_FIELD.get((0, 0))   # USA CS
        de_sal  = SALARY_BY_COUNTRY_FIELD.get((1, 0))   # Germany CS
        assert usa_sal > de_sal
