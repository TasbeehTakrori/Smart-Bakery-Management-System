from sqlalchemy import Column, Integer, String, DateTime

from models.base import Base

class CheckpointCondition(Base):
    __tablename__ = "checkpoint_conditions"

    date = Column(DateTime, primary_key=True)
    cp_1 = Column(Integer)
    cp_2 = Column(Integer)
    cp_3 = Column(Integer)
    cp_4 = Column(Integer)
    cp_5 = Column(Integer)

    def __repr__(self):
        return f"<CheckpointCondition(date={self.date}, cp_1={self.cp_1}, cp_2={self.cp_2}, cp_3={self.cp_3}, cp_4={self.cp_4}, cp_5={self.cp_5})>"