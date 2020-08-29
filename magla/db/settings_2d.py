from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .. import __base__
# from .toolconfig import ToolConfig


class Settings2D(__base__):
    __tablename__ = "settings_2d"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Settings2D"

    id = Column(Integer, primary_key=True)
    width = Column(Integer)
    height = Column(Integer)
    rate = Column(Float)
    color_profile = Column(String)

    project = relationship("Project")
