from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .. import __base__


class Timeline(__base__):
    __tablename__ = "timelines"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Timeline"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    label = Column(String)
    otio = Column(JSONB)

    user = relationship("User", uselist=False, back_populates="timelines")
