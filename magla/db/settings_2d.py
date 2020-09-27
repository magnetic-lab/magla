from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Settings2D(MaglaORM._Base):
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
