from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user model containing common user attributes."""

    id: UUID | None = None
    """Unique identifier for the user. Defaults to None."""

    email: EmailStr | None = None
    """User's email address. Must be a valid email format."""

    avatar_url: str | None = None
    """URL to the user's profile picture or avatar."""

    first_name: str
    """User's first name. Required field."""

    last_name: str
    """User's last name. Required field."""

    provider: str | None = None
    """Authentication provider (e.g., 'google', 'github', etc.) if user signed up via OAuth."""

    confirmed_at: datetime | None = None
    """Timestamp when the user confirmed their email address."""

    verified: bool = False
    """Whether the user's account has been verified. Defaults to False."""

    verified_at: datetime | None = None
    """Timestamp when the user's account was verified."""


class UserCreate(UserBase):
    """Schema for creating a new user. Inherits all fields from UserBase."""


class UserOnboard(UserBase):
    """Schema for onboarding a new user with external authentication."""

    external_id: str
    """Unique identifier from the external authentication provider."""


class UserUpdate(BaseModel):
    """Schema for updating an existing user. All fields are optional."""

    email: EmailStr | None = None
    """Updated email address. Must be a valid email format."""

    avatar_url: str | None = None
    """Updated avatar URL."""

    first_name: str | None = None
    """Updated first name."""

    last_name: str | None = None
    """Updated last name."""

    provider: str | None = None
    """Updated authentication provider."""

    verified: bool | None = None
    """Updated verification status."""

    verified_at: datetime | None = None
    """Updated verification timestamp."""


class UserInDB(UserBase):
    """Schema representing a user as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the user in the database."""

    created_at: datetime
    """Timestamp when the user record was created."""

    updated_at: datetime
    """Timestamp when the user record was last updated."""

    model_config = {"from_attributes": True}


class User(UserInDB):
    """Schema for user data returned in API responses. Inherits all fields from UserInDB."""


class UserDetails(BaseModel):
    """Schema for detailed user information, typically used in profile views."""

    id: UUID
    """Unique identifier for the user."""

    email: EmailStr
    """User's email address. Required and must be a valid email format."""

    avatar_url: str | None = None
    """URL to the user's profile picture or avatar."""

    first_name: str
    """User's first name. Required field."""

    last_name: str
    """User's last name. Required field."""

    provider: str | None = None
    """Authentication provider used by the user."""

    verified: bool = False
    """Whether the user's account has been verified. Defaults to False."""

    verified_at: datetime | None = None
    """Timestamp when the user's account was verified."""

    model_config = {"from_attributes": True}
