from datetime import datetime

from sqlalchemy import Column, Integer, DateTime

from .base import Base


class AutoRole(Base):
    __tablename__ = 'autorole'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer)
    role_id = Column(Integer, unique=True)
    created = Column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"AutoRole(guild_id={self.guild_id}, "
            f"role_id={self.role_id})"
        )
