from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Project(MaglaORM._Base):
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Project"

    id = Column(Integer, primary_key=True)
    directory_id = Column(Integer, ForeignKey("directories.id"))
    timeline_id = Column(Integer, ForeignKey("timelines.id"))
    name = Column(String)
    settings = Column(JSON)

    timeline = relationship("Timeline")
    settings_2d = relationship("Settings2D", uselist=False, back_populates="project")
    episodes = relationship("Episode", back_populates="project")
    sequences = relationship("Sequence", back_populates="project")
    shots = relationship("Shot", back_populates="project")
    tool_configs = relationship("ToolConfig", back_populates="project")
    directory = relationship("Directory")
