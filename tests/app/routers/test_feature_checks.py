"""Feature Check API tests.

The global test harness patches tessera_sdk's `authorize()` to always allow
(see tests/conftest.py), so actor-domain isolation and admin/check
permission separation can't be observed through that blanket mock. These
tests instead override the exact dependency object the router wired up
(`feature_checks.rbac["read"]` / `features.rbac["read"]`) with a
domain-aware fake so the real routing behaviour -- which Custos domain gets
authorized for which route -- is exercised end-to-end.
"""

from fastapi import HTTPException, Request, status

from app.routers import feature_checks, features


def _authorize_only_domain(allowed_domain: str):
    async def dependency(request: Request):
        actor_id = request.query_params.get("actor_id")
        domain = actor_id if actor_id else "*"
        if domain != allowed_domain:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return True

    return dependency


def _always_deny(request: Request):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


def test_actor_scoped_check_denies_a_different_actor(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})
    client.post(f"/features/{key}/gates/actors/actor-a")

    app = client.app
    app.dependency_overrides[feature_checks.rbac["read"]] = _authorize_only_domain(
        "actor-a"
    )
    try:
        allowed = client.get(f"/feature-checks/{key}", params={"actor_id": "actor-a"})
        assert allowed.status_code == 200
        assert allowed.json()["enabled"] is True

        denied = client.get(f"/feature-checks/{key}", params={"actor_id": "actor-b"})
        assert denied.status_code == 403
    finally:
        del app.dependency_overrides[feature_checks.rbac["read"]]


def test_omitted_actor_id_authorizes_against_global_domain(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})
    client.post(f"/features/{key}/gates/boolean")

    app = client.app
    app.dependency_overrides[feature_checks.rbac["read"]] = _authorize_only_domain("*")
    try:
        response = client.get(f"/feature-checks/{key}")
        assert response.status_code == 200
        assert response.json()["enabled"] is True
    finally:
        del app.dependency_overrides[feature_checks.rbac["read"]]


def test_empty_actor_id_is_rejected_with_422(client, faker):
    key = faker.slug()
    client.post("/features", json={"key": key})

    response = client.get(f"/feature-checks/{key}", params={"actor_id": ""})
    assert response.status_code == 422


def test_unknown_feature_key_returns_disabled_not_error(client):
    response = client.get("/feature-checks/does-not-exist")
    assert response.status_code == 200
    assert response.json() == {"key": "does-not-exist", "enabled": False}


def test_enabled_features_omits_disabled_features(client, faker):
    enabled_key = faker.slug()
    disabled_key = faker.slug()
    client.post("/features", json={"key": enabled_key})
    client.post(f"/features/{enabled_key}/gates/boolean")
    client.post("/features", json={"key": disabled_key})

    response = client.get("/enabled-features")

    assert response.status_code == 200
    keys = response.json()["features"]
    assert enabled_key in keys
    assert disabled_key not in keys


def test_feature_check_permission_does_not_grant_admin_access(client):
    """feature_check being authorized must not imply feature_admin is."""
    app = client.app
    app.dependency_overrides[features.rbac["read"]] = _always_deny
    try:
        admin_response = client.get("/features")
        assert admin_response.status_code == 403

        check_response = client.get("/feature-checks/whatever")
        assert check_response.status_code == 200
    finally:
        del app.dependency_overrides[features.rbac["read"]]


def test_feature_admin_permission_is_not_required_for_actor_checks(client):
    """feature_admin being denied must not affect feature_check routes."""
    app = client.app
    app.dependency_overrides[features.rbac["create"]] = _always_deny
    app.dependency_overrides[features.rbac["update"]] = _always_deny
    try:
        check_response = client.get(
            "/feature-checks/whatever", params={"actor_id": "actor-1"}
        )
        assert check_response.status_code == 200
    finally:
        del app.dependency_overrides[features.rbac["create"]]
        del app.dependency_overrides[features.rbac["update"]]
