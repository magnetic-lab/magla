from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Episode(MaglaORM._Base):
    __tablename__ = "episodes"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Episode"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    name = Column(String)
    otio = Column(JSONB)

    project = relationship("Project", uselist=False, back_populates="episodes")
    sequences = relationship("Sequence", back_populates="episode")
    shots = relationship("Shot", back_populates="episode")
    directory = relationship("Directory")
