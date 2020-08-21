from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from .. import __base__


class Dependency(__base__):
    __tablename__ = "dependencies"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Dependency"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String)
    package = Column(JSONB)

