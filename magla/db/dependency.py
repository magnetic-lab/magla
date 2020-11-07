from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON

from ..db.orm import MaglaORM


class Dependency(MaglaORM._Base):
    __tablename__ = "dependencies"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Dependency"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String)
    package = Column(JSON)
