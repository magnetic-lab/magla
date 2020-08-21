from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .. import __base__
# from .toolconfig import ToolConfig


class Project(__base__):
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Project"

    id = Column(Integer, primary_key=True)
    settings_2d_id = Column(Integer, ForeignKey("settings_2d.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    name = Column(String)
    path = Column(String)
    otio = Column(JSONB)
    custom_settings = Column(JSONB)


    settings_2d = relationship("Settings2D")
    shots = relationship("Shot", back_populates="project")
    tool_configs = relationship("ToolConfig", back_populates="project")
    directory = relationship("Directory")
