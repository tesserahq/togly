## Problem Statement

Backend applications, starting with linden-api, need a way to turn features on or off and
enable them for specific actors without hardcoding that logic, redeploying to flip a flag,
or building bespoke flag storage in each application.

Today togly has no feature-flag capability. It is being built as the organization's shared
feature-flag service, modeled on the feature and gate concepts from Ruby's `flipper` gem.

## Solution

Togly owns a Postgres schema for features, actor gates, and audit logs and exposes an HTTP
API. The first client is added to `tessera_sdk` and consumed by linden-api.

For v1:

- A **feature** is a uniquely named flag with a global boolean gate and zero or more actor
  gates. Percentage, group, expression, and time-based gates are deferred.
- There is one global feature-key namespace. Project or organization namespacing of feature
  keys is not part of v1.
- Flag changes and their audit records are written atomically in a single transaction: if
  the audit write fails, the flag mutation rolls back with it. The audit log exists for
  incident forensics ("who turned this off?"), so a mutation is never allowed to succeed
  without its audit record — no separate-transaction failure mode to detect or repair.
- linden-api authenticates through the existing `tessera_sdk` machine-to-machine token and
  RBAC path.
- Each feature check is a live HTTP request. There is no client-side flag cache or local gate
  logic. The SDK uses a short timeout and returns a caller-supplied default only for network
  failures, timeouts, and server-side 5xx responses.
- Administrative operations use the `togly.feature_admin` RBAC resource in the global
  domain. Feature checks use `togly.feature_check`: when the caller supplies an `actor_id`,
  that value is the Custos domain; `actor_id` is optional, and a check with none supplied
  authorizes against the global domain and evaluates only the feature's boolean gate (actor
  gates never apply without an actor to match). These permissions are deliberately separate
  from `togly.feature_admin`.
- The browser/JS SDK and linden-portal integration are deferred until the server and Python
  client are established.

## User Stories

1. As a togly admin, I want to create a feature with a unique key so client applications can
   reference it before it is enabled.
2. As a togly admin, I want to enable a feature globally so it is on for every actor.
3. As a togly admin, I want to disable a feature globally without deleting its actor-gate
   configuration so I can stop a rollout during an incident. The precise override semantics
   remain an open design question.
4. As a togly admin, I want to enable a feature for a specific actor id so selected projects
   or users can receive it before broader release.
5. As a togly admin, I want to remove a specific actor from a feature without affecting other
   actors.
6. As a togly admin, I want to delete a feature after its checks have been removed from client
   applications.
7. As a togly admin, I want to list features and their current gate configuration.
8. As a togly admin, I want every mutation and its audit entry (immutable feature id,
   feature key, acting user, action, timestamp) to succeed or fail together, so a flag
   change can never exist without a matching audit record.
9. As a togly admin, I want to view the audit history for one feature incarnation, even after
   that feature is deleted or its key is later reused.
10. As a linden-api developer, I want a Python client in `tessera_sdk` that checks one
    feature or lists an actor's enabled feature keys so application code does not hand-roll
    HTTP or authentication.
11. As a linden-api developer, I want network failures, timeouts, and togly 5xx responses to
    return a caller-supplied default without raising.
12. As a linden-api developer, I want 401, 403, and other caller errors to remain visible so
    authentication, authorization, and contract bugs are not converted into flag values.
13. As a togly operator, I want administrative and actor-check permissions to be separate so
    the ability to check a project's flags never grants access to flag configuration or audit
    history.
14. As a togly operator, I want an actor check to require authorization for that exact actor
    domain.
15. As a linden-api developer, I want to check a purely global feature (boolean gate only, no
    actor semantics) without supplying an actor id, so I don't have to invent a placeholder
    value just to satisfy the check API.
16. As a togly operator, I want linden-api's service account to hold a global
    `togly.feature_check/read` grant so it can check flags for projects that linden-api has
    already authorized.

## Implementation Decisions

- **Service identity**: before feature work, replace inherited service defaults with Togly
  identities for the package, application, database, test database, telemetry, RBAC,
  Redis, container image, and worker configuration.
- **Models**: `Feature` has a unique key and timestamps. `Gate` belongs to a feature and is
  either `boolean` or `actor`. `FeatureAuditLog` stores both immutable `feature_id` and the
  denormalized `feature_key`, plus acting user, action, snapshot, and timestamp.
- **Repositories**: `FeatureRepository`, `GateRepository`, and
  `FeatureAuditLogRepository` follow the existing repository layer. Features are hard
  deleted; their gates cascade-delete, while audit rows survive.
- **Commands**: one command handles each mutation. The feature/gate mutation and its audit
  entry are written and committed together in a single transaction; if the audit write
  fails, the whole mutation rolls back and the caller sees an error rather than a
  successful response with a missing audit trail.
- **Queries**: admin list/detail/audit queries are separate from `CheckFeatureQuery` and
  `ListEnabledFeaturesQuery`. The latter returns only enabled feature keys; disabled
  features are omitted. Admin feature responses expose immutable feature IDs, and
  audit history is fetched by that ID so deleted or key-reused feature incarnations remain
  distinguishable.
- **Gate checker**: one pure server-side component evaluates the global boolean state and
  actor membership. SDKs contain no evaluation logic.
- **Routers**: administrative routes remain under `/features` and use
  `togly.feature_admin`; audit history uses
  `GET /feature-audit-logs/{feature_id}` under the same permission. Single-feature checks
  use `GET /feature-checks/{key}?actor_id=...`; enabled-feature discovery uses
  `GET /enabled-features?actor_id=...` and returns enabled keys only.
  `actor_id` is optional: when supplied, it's authorized through `togly.feature_check` in
  that exact Custos domain and both boolean and actor gates are evaluated; when omitted,
  the check authorizes against the global domain and evaluates only the boolean gate
  (actor gates cannot match without an actor).
- **SDK**: the Python client is implemented in `tessera_sdk`, reuses its existing
  `AuthTokenProvider`, and is versioned and released there. Togly does not enable the
  `tessera_sdk` authorization cache (`AUTHORIZATION_CACHE_ENABLED` stays at its default of
  `false`) because the currently pinned build's cache reads `authorized` but writes
  `allowed`, so a cache hit always incorrectly denies. This isn't a release blocker for v1
  — caching is opt-in and off by default — but the cache should stay disabled until the fix
  is confirmed merged upstream, at which point togly can revisit enabling it.
- **Schema**: `features`, `gates`, and `feature_audit_logs` are added through Alembic on top
  of the reset migration history.

## Testing Decisions

- **Gate checker**: boolean enabled/disabled, actor present/absent, no actor supplied
  (global-only evaluation), and no configured gates.
- **Commands**: verify the mutation and its audit entry commit together — assert that a
  forced audit-write failure rolls back the mutation too, not just that both succeed
  independently.
- **Audit history**: delete and recreate the same key and confirm each incarnation is queried
  by its immutable `feature_id`.
- **Repositories**: use the real PostgreSQL test database with `ENV=test`.
- **Authorization resources**: prove that `feature_check` does not grant access to admin
  routes and that `feature_admin` is not implicitly required for actor checks.
- **Actor scoping**: a caller authorized for actor A receives 403 for actor B; a check with
  no `actor_id` authorizes against the global domain instead.
- **SDK errors**: defaults are returned for timeout/network/5xx only; 401, 403, and other 4xx
  errors remain visible.
- **Authorization cache stays off**: a smoke test confirms togly runs with
  `AUTHORIZATION_CACHE_ENABLED` unset/false, so the known cache read/write key mismatch in
  the pinned `tessera_sdk` build can't cause spurious 403s in v1.

## Out of Scope

- Percentage, group, expression, and percentage-of-time gates.
- Project or organization namespacing of feature keys.
- Client-side flag caching or polling.
- Browser access, a JS/TS SDK, linden-portal integration, and CORS configuration.
- A dedicated admin UI.

## Open Questions

- Define the global enable/disable override semantics required by user story 3, including
  how an administrator returns a force-disabled feature to actor-gated behavior without
  deleting the saved actor gates.

No other product questions currently block the server and Python SDK work. See
`docs/designs/0001-feature-flag-service-design.md` for the technical design.
