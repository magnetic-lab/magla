from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .. import __base__


class Facility(__base__):
    __tablename__ = "facilities"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Facility"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    repo_dir = Column(String)
    magla_dir = Column(String)
    custom_settings = Column(JSONB)

    machines = relationship("Machine", back_populates="facility")
