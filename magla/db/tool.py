from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from .. import __base__


class Tool(__base__):
    __tablename__ = "tools"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Tool"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    metadata_ = Column(JSONB)

    versions = relationship("ToolVersion", back_populates="tool")
    aliases = relationship("ToolAlias", back_populates="tool")
