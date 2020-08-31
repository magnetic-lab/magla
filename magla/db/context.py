from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .user import User
from ..db.orm import MaglaORM


class Context(MaglaORM.BASE):
    __tablename__ = "contexts"
    __table_args__ = {'extend_existing': True}
    __entity_name__ = "Context"

    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"))

    machine = relationship("Machine", uselist=False, back_populates="contexts")
    user = relationship("User", uselist=False, back_populates="context")
    assignment = relationship("Assignment", uselist=False)
