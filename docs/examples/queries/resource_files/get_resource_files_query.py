from typing import Any
from uuid import UUID

from app.repositories.resource_file_repository import ResourceFileRepository
from app.schemas.resource_file import ResourceFileWithMetadata
from pydantic import BaseModel
from sqlalchemy.orm import Session
from tessera_sdk.clients.vaulta import VaultaClient  # type: ignore[import-untyped]
from tessera_sdk.infra.auth_token_provider import (
    AuthTokenProvider,  # type: ignore[import-untyped]
)

from app.config import get_settings


class GetResourceFilesQuery:
    """
    Query to retrieve resource files for any entity using the generic repository method.
    """

    def __init__(self, db: Session):
        self.db = db
        self.resource_file_service = ResourceFileRepository(db)

    def execute(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ResourceFileWithMetadata]:
        """
        Retrieve resource files for a given entity.

        Returns enriched `ResourceFileWithMetadata` objects (resource + Vaulta metadata).
        """

        resource_files = self.resource_file_service.get_resource_files_for(
            entity_type=entity_type,
            entity_id=entity_id,
            skip=skip,
            limit=limit,
        )

        return self.enrich(resource_files)

    def enrich(self, resource_files: list[Any]) -> list[ResourceFileWithMetadata]:
        """Attach Vaulta metadata to a list of ResourceFile ORM objects.

        Used directly as a fastapi_pagination `transformer` so metadata is only
        fetched for the current page, not the entire result set.
        """
        vaulta_client = self._get_vaulta_client()

        enriched_files: list[ResourceFileWithMetadata] = []
        for rf in resource_files:
            resource_metadata = self._get_resource_metadata(
                UUID(str(rf.resource_id)), vaulta_client
            )
            rf.metadata = resource_metadata  # type: ignore[attr-defined]
            enriched_files.append(ResourceFileWithMetadata.model_validate(rf))

        return enriched_files

    def _get_vaulta_client(self) -> VaultaClient | None:
        """Build a single Vaulta client to reuse (and keep its connection alive)
        across every resource file in a page, instead of one per file."""

        settings = get_settings()
        # Never call external services during tests, and allow opt-out if disabled
        if settings.is_test or not settings.vaulta_enabled:
            return None

        return VaultaClient(
            base_url=settings.vaulta_internal_api_url_or_default,
            api_token=self._get_auth_token(),
        )

    def _get_resource_metadata(
        self, resource_id: UUID, vaulta_client: VaultaClient | None
    ) -> dict:
        """Get the metadata for a resource."""

        if vaulta_client is None:
            return {}

        # get_asset may return an object (e.g., AssetResponse). Convert to plain dict.
        asset = vaulta_client.get_asset(str(resource_id))
        return self._as_dict(asset)

    def _as_dict(self, obj: Any) -> dict:
        """Convert Vaulta asset response (Pydantic) to a plain dict."""
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return {}

    def _get_auth_token(self) -> str:
        """Get an M2M token for Vaulta API."""
        return AuthTokenProvider().get_token()
