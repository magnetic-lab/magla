from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class ShotVersion(MaglaORM.BASE):
    __tablename__ = "shot_versions"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "ShotVersion"

    id = Column(Integer, primary_key=True)
    shot_id = Column(Integer, ForeignKey("shots.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    num = Column(Integer)
    otio = Column(JSONB)

    assignment = relationship("Assignment", uselist=False, back_populates="shot_version")
    shot = relationship("Shot", uselist=False, back_populates="versions")
    directory = relationship("Directory")
