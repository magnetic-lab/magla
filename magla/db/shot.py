from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Shot(MaglaORM._Base):
    __tablename__ = "shots"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Shot"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    name = Column(String)
    otio = Column(JSONB)
    track_index = Column(Integer)
    start_frame_in_parent = Column(Integer)

    project = relationship("Project", uselist=False, back_populates="shots")
    versions = relationship("ShotVersion", back_populates="shot")
    directory = relationship("Directory")
