from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class FileType(MaglaORM._Base):
    __tablename__ = "file_types"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "FileType"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    extensions = Column(JSON)
    description = Column(String(100))

    tool_versions = relationship("ToolVersion", back_populates="file_types")
