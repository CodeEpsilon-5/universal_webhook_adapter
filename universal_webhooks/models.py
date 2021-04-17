import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils.types import URLType

from universal_webhooks.database import Base


class Adapter(Base):
    __tablename__ = "adapters"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    send_to = Column(URLType, nullable=False)
    translation_query = Column(String, nullable=False)
    last_access = Column(DateTime, default=datetime.now)
