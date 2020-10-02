from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Assignment(MaglaORM._Base):
    __tablename__ = "assignments"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Assignment"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    shot_version_id = Column(Integer, ForeignKey("shot_versions.id"))

    shot_version = relationship("ShotVersion")
    user = relationship("User", uselist=False, back_populates="assignments")
