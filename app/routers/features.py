from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from tessera_sdk.server.dependencies.auth import get_current_user

from app.auth.rbac import build_rbac_dependencies
from app.commands.feature.create_feature_command import CreateFeatureCommand
from app.commands.feature.delete_feature_command import DeleteFeatureCommand
from app.commands.feature.disable_actor_gate_command import DisableActorGateCommand
from app.commands.feature.disable_boolean_gate_command import DisableBooleanGateCommand
from app.commands.feature.enable_actor_gate_command import EnableActorGateCommand
from app.commands.feature.enable_boolean_gate_command import EnableBooleanGateCommand
from app.db import get_db
from app.models.user import User
from app.queries.feature.get_feature_query import GetFeatureQuery
from app.queries.feature.list_features_query import ListFeaturesQuery
from app.schemas.feature import (
    ActorGateRequest,
    FeatureCreate,
    FeatureKey,
    FeatureResponse,
    GateResponse,
)

router = APIRouter(prefix="/features", tags=["features"])

rbac = build_rbac_dependencies(resource="feature_admin")


@router.post(
    "",
    response_model=FeatureResponse,
    status_code=201,
    dependencies=[Depends(rbac["create"])],
)
def create_feature(
    payload: FeatureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CreateFeatureCommand(db).execute(payload, created_by=current_user)


@router.get(
    "",
    response_model=Page[FeatureResponse],
    dependencies=[Depends(rbac["read"])],
)
def list_features(db: Session = Depends(get_db)):
    return paginate(ListFeaturesQuery(db).execute())


@router.get(
    "/{key}",
    response_model=FeatureResponse,
    dependencies=[Depends(rbac["read"])],
)
def get_feature(key: str, db: Session = Depends(get_db)):
    return GetFeatureQuery(db, key).execute()


@router.delete(
    "/{key}",
    status_code=204,
    dependencies=[Depends(rbac["delete"])],
)
def delete_feature(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    DeleteFeatureCommand(db).execute(FeatureKey(key=key), deleted_by=current_user)


@router.post(
    "/{key}/gates/boolean",
    response_model=GateResponse,
    dependencies=[Depends(rbac["update"])],
)
def enable_boolean_gate(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return EnableBooleanGateCommand(db).execute(
        FeatureKey(key=key), modified_by=current_user
    )


@router.delete(
    "/{key}/gates/boolean",
    status_code=204,
    dependencies=[Depends(rbac["update"])],
)
def disable_boolean_gate(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    DisableBooleanGateCommand(db).execute(FeatureKey(key=key), modified_by=current_user)


@router.post(
    "/{key}/gates/actors/{actor_id}",
    response_model=GateResponse,
    dependencies=[Depends(rbac["update"])],
)
def enable_actor_gate(
    key: str,
    actor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return EnableActorGateCommand(db).execute(
        ActorGateRequest(key=key, actor_id=actor_id), modified_by=current_user
    )


@router.delete(
    "/{key}/gates/actors/{actor_id}",
    status_code=204,
    dependencies=[Depends(rbac["update"])],
)
def disable_actor_gate(
    key: str,
    actor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    DisableActorGateCommand(db).execute(
        ActorGateRequest(key=key, actor_id=actor_id), modified_by=current_user
    )
