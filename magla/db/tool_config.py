from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class ToolConfig(MaglaORM._Base):
    """A single configuration for a tool, usually specific to the Project."""
    __tablename__ = "tool_configs"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "ToolConfig"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    tool_version_id = Column(Integer, ForeignKey("tool_versions.id"))
    env = Column(JSONB)
    copy_dict = Column(JSONB)

    project = relationship("Project", uselist=False, back_populates="tool_configs")
    tool_version = relationship("ToolVersion", uselist=False, back_populates="tool_config")
