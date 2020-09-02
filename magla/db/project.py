from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Project(MaglaORM.BASE):
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Project"

    id = Column(Integer, primary_key=True)
    settings_2d_id = Column(Integer, ForeignKey("settings_2d.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    timeline_id = Column(Integer, ForeignKey("timelines.id"))
    name = Column(String)
    path = Column(String)
    settings = Column(JSONB)

    timeline = relationship("Timeline")
    settings_2d = relationship("Settings2D")
    shots = relationship("Shot", back_populates="project")
    tool_configs = relationship("ToolConfig", back_populates="project")
    directory = relationship("Directory")
