"""Service identity and authorization-cache smoke tests.

See docs/prds/0001-feature-flag-service.md, "Implementation Decisions" and
docs/designs/0001-feature-flag-service-design.md, "Authorization-cache bug".
"""

from app.config import get_settings


def test_service_identifiers_use_togly_names():
    settings = get_settings()

    assert settings.app_name == "togly-api"
    assert settings.otel_service_name == "togly"
    assert settings.db_app_name == "togly-api"
    assert "togly" in settings.database_url


def test_authorization_cache_stays_disabled_by_default():
    """
    tessera_sdk's authorization cache write path stores key `allowed` but
    the cache-hit read path checks `authorized`, so any cache hit
    incorrectly denies a previously-granted request. Togly must not set
    AUTHORIZATION_CACHE_ENABLED until that upstream fix is confirmed merged.
    """
    from tessera_sdk.config import get_settings as get_sdk_settings

    sdk_settings = get_sdk_settings()
    assert sdk_settings.authorization_cache_enabled is False
