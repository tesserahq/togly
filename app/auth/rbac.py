from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, status
from tessera_sdk.server.dependencies.authorization import authorize

DomainResolver = Callable[[Request], Awaitable[str]]

PREFIX = "togly"


class RBACActions:
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


async def actor_domain(request: Request) -> str:
    """
    RBAC domain resolver for Feature Check routes.

    When the caller supplies an `actor_id` query parameter, that exact value
    is the Custos domain, so a caller authorized for actor A cannot check
    actor B. An omitted `actor_id` authorizes against the global domain and
    only the feature's boolean gate is evaluated (actor gates never match
    without an actor). A present-but-empty `actor_id` is rejected as
    malformed by the route itself before this resolver is consulted.
    """
    actor_id = request.query_params.get("actor_id")
    if actor_id is not None and actor_id == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="actor_id must not be empty",
        )
    return actor_id if actor_id else "*"


async def global_domain(_: Request) -> str:
    """
    RBAC domain resolver for resources with no per-tenant domain concept.

    Togly has no existing project/tenant model of its own (unlike Sendly,
    which authorizes per its own project_id). Campaign.project_id is Sendly's
    domain, nullable, and not a Togly tenant boundary, so it isn't a
    meaningful RBAC domain here — authorize against a fixed wildcard domain
    instead, mirroring Sendly's own fallback (`project_id or "*"`).
    """
    return "*"


def build_rbac_dependencies(
    *, resource: str, domain_resolver: DomainResolver = global_domain
):
    return {
        "create": authorize(
            resource=f"{PREFIX}.{resource}",
            action=RBACActions.CREATE,
            domain_resolver=domain_resolver,
        ),
        "read": authorize(
            resource=f"{PREFIX}.{resource}",
            action=RBACActions.READ,
            domain_resolver=domain_resolver,
        ),
        "update": authorize(
            resource=f"{PREFIX}.{resource}",
            action=RBACActions.UPDATE,
            domain_resolver=domain_resolver,
        ),
        "delete": authorize(
            resource=f"{PREFIX}.{resource}",
            action=RBACActions.DELETE,
            domain_resolver=domain_resolver,
        ),
    }
