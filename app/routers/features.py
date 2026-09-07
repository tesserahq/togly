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
from app.schemas.feature import FeatureCreate, FeatureResponse, GateResponse

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
    feature = CreateFeatureCommand(
        db, key=payload.key, description=payload.description, current_user=current_user
    ).execute()
    return feature


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
    DeleteFeatureCommand(db, feature_key=key, current_user=current_user).execute()


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
    return EnableBooleanGateCommand(
        db, feature_key=key, current_user=current_user
    ).execute()


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
    DisableBooleanGateCommand(db, feature_key=key, current_user=current_user).execute()


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
    return EnableActorGateCommand(
        db, feature_key=key, actor_id=actor_id, current_user=current_user
    ).execute()


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
    DisableActorGateCommand(
        db, feature_key=key, actor_id=actor_id, current_user=current_user
    ).execute()
