from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class User(MaglaORM._Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "User"

    id = Column(Integer, primary_key=True)

    first_name = Column(String)
    last_name = Column(String)
    nickname = Column(String)
    email = Column(String)

    context = relationship("Context", uselist=False, back_populates="user")
    assignments = relationship("Assignment", back_populates="user")
    directories = relationship("Directory", back_populates="user")
    timelines = relationship("Timeline", back_populates="user")
