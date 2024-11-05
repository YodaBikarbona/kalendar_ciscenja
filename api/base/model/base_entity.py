from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
)

from api.base.database_connector import Base
from api.utils.utils import now


class BaseEntity(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, name="id")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=now(), name="created_at")
    modified_at = Column(TIMESTAMP(timezone=True), nullable=False, default=now(), onupdate=now(), name="modified_at")

    def get_id(self):
        return self.id

    def get_created_at(self):
        return self.created_at

    def get_modified_at(self):
        return self.modified_at
