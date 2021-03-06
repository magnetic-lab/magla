from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Timeline(MaglaORM._Base):
    __tablename__ = "timelines"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Timeline"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    label = Column(String)
    otio = Column(JSON)

    user = relationship("User", uselist=False, back_populates="timelines")
