from uuid import uuid4
from datetime import datetime, timedelta
from email.policy import default
from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base


# Archive Model
class Archive(Base):
    __tablename__ = 'archives'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid4)
    title = Column(String(255), index=True, unique=True, nullable=False)
    description = Column(Text, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete="SET NULL"))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    author = relationship("User")


# User Model
class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid4)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255))

    firstname = Column(String(255), nullable=False, index=True)
    lastname = Column(String(255), nullable=False, index=True)
    middlename = Column(String(255), index=True)
    is_active = Column(Boolean, server_default='TRUE', nullable=False)

    photo_url = Column(Text)
    refresh_token = Column(String(255))
    roles = Column(ARRAY(String(255)))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))


# Role Model
class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid4)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255))
    author_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete="SET NULL"))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    author = relationship("User")

# Permission Model


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid4)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255))

    role_id = Column(UUID(as_uuid=True), ForeignKey(
        'roles.id', ondelete="SET NULL"))
    author_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete="SET NULL"))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    role = relationship("Role")
    author = relationship("User")


# Workspace Model
class Workspace(Base):
    __tablename__ = 'workspaces'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid4)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255))
    description = Column(Text, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete="SET NULL"))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    author = relationship("User")


# Reset Code Model
class ResetCode(Base):
    __tablename__ = 'reset_codes'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid4)
    email = Column(String, index=True)
    reset_code = Column(String, index=True, nullable=False)
    expires_in = Column(DateTime, default=datetime.now() + timedelta(hours=2))
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete="SET NULL"))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    user = relationship("User")
