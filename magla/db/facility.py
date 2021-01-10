from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Facility(MaglaORM._Base):
    __tablename__ = "facilities"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Facility"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    settings = Column(JSONB)

    machines = relationship("Machine", back_populates="facility")
