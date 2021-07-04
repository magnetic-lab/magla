from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Tool(MaglaORM._Base):
    __tablename__ = "tools"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Tool"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    versions = relationship("ToolVersion", back_populates="tool")
