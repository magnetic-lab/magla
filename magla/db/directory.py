from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..db.orm import MaglaORM


class Directory(MaglaORM.BASE):
    __tablename__ = "directories"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Directory"

    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    label = Column(String)
    path = Column(String)
    tree = Column(JSONB)
    bookmarks = Column(JSONB)

    machine = relationship("Machine", uselist=False, back_populates="directories")
    user = relationship("User", uselist=False, back_populates="directories")
