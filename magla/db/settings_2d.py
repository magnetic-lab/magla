from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM
# from .toolconfig import ToolConfig


class Settings2D(MaglaORM.BASE):
    __tablename__ = "settings_2d"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Settings2D"

    id = Column(Integer, primary_key=True)
    label = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    rate = Column(Float)
    color_profile = Column(String)

    project = relationship("Project")
