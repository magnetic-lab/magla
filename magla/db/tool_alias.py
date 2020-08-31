from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import ARRAY
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class ToolAlias(MaglaORM.BASE):
    __tablename__ = "tool_aliases"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "ToolAlias"

    id = Column(Integer, primary_key=True)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    alias = Column(String)

    tool = relationship("Tool", uselist=False, back_populates="aliases")
