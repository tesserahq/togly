import pytest
from fastapi import HTTPException, Request


def _request_with_query(query_string: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "query_string": query_string.encode(),
        "headers": [],
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_actor_domain_returns_actor_id_when_present():
    from app.auth.rbac import actor_domain

    domain = await actor_domain(_request_with_query("actor_id=actor-1"))
    assert domain == "actor-1"


@pytest.mark.asyncio
async def test_actor_domain_falls_back_to_global_when_absent():
    from app.auth.rbac import actor_domain

    domain = await actor_domain(_request_with_query(""))
    assert domain == "*"


@pytest.mark.asyncio
async def test_actor_domain_rejects_empty_actor_id():
    from app.auth.rbac import actor_domain

    with pytest.raises(HTTPException) as exc_info:
        await actor_domain(_request_with_query("actor_id="))
    assert exc_info.value.status_code == 422


def test_feature_admin_and_feature_check_use_separate_resources():
    from app.routers.feature_checks import rbac as check_rbac
    from app.routers.features import rbac as admin_rbac

    # Both dicts are distinct dependency-callable objects even though they
    # share an action set, proving the two RBAC resources aren't wired to
    # the same authorization dependency.
    assert admin_rbac["read"] is not check_rbac["read"]
