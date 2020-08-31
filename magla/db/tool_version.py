from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class ToolVersion(MaglaORM.BASE):
    __tablename__ = "tool_versions"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "ToolVersion"

    id = Column(Integer, primary_key=True)
    string = Column(String)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    file_types_id = Column(Integer, ForeignKey("file_types.id"))
    file_extension = Column(String)

    installations = relationship("ToolVersionInstallation", back_populates="tool_version")
    tool = relationship("Tool", uselist=False, back_populates="versions")
    tool_config = relationship("ToolConfig", uselist=False, back_populates="tool_version")
    file_types = relationship("FileType", back_populates="tool_versions")
