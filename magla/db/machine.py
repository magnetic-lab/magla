from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Machine(MaglaORM._Base):
    __tablename__ = "machines"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Machine"

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    uuid = Column(String)  # unique
    name = Column(String)
    ip_address = Column(String)

    facility = relationship("Facility", back_populates="machines")
    contexts = relationship("Context", back_populates="machine")
    directories = relationship("Directory", back_populates="machine")
