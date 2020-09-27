from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class ToolVersionInstallation(MaglaORM._Base):
    __tablename__ = "tool_version_installations"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "ToolVersionInstallation"

    id = Column(Integer, primary_key=True)
    tool_version_id = Column(Integer, ForeignKey("tool_versions.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))

    tool_version = relationship("ToolVersion", uselist=False, back_populates="installations")
    directory = relationship("Directory")
