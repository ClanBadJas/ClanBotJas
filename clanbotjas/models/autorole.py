from datetime import datetime

from sqlalchemy import Column, DateTime, BigInteger

from .base import Base


class AutoRole(Base):
    __tablename__ = 'autorole'

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    role_id = Column(BigInteger, nullable=False, unique=True)
    created = Column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"AutoRole(guild_id={self.guild_id}, "
            f"role_id={self.role_id})"
        )
