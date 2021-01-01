from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Sequence(MaglaORM._Base):
    __tablename__ = "sequences"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Sequence"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    name = Column(String)
    otio = Column(JSON)

    project = relationship("Project", uselist=False, back_populates="sequences")
    episode = relationship("Episode", uselist=False, back_populates="sequences")
    shots =  relationship("Shot", back_populates="sequence")
    directory = relationship("Directory")
