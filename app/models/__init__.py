"""
Models package - imports all models to ensure SQLAlchemy can resolve relationships.
This ensures all models are loaded before SQLAlchemy initializes mappers.
"""

# Import all models to ensure they're registered with SQLAlchemy
# Order matters to avoid circular import issues, but string-based relationships help

# Base models (no dependencies)
from app.models.party import Party
from app.models.state_mstr import UserMstr

# Models that depend on Party
from app.models.user import User

# Models that depend on User
from app.models.project import Project
from app.models.audit_event import AuditEvent

# Models that depend on Project
from app.models.document import Document
from app.models.access_grant import AccessGrant
from app.models.allocation import Allocation

# Models that depend on Commitment
from app.models.settlement_log import SettlementLog

# Standalone models
from app.models.invitation import Invitation

# Export all models for convenience
__all__ = [
    "Party",
    "User",
    "Project",
    "Document",

    "AccessGrant",
    "Allocation",
    "SettlementLog",
    "AuditEvent",
    "Invitation",
    "UserMstr",
]

