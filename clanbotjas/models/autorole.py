from datetime import datetime

from sqlalchemy import Column, DateTime, BigInteger, ForeignKey

from .base import Base


class AutoRole(Base):
    __tablename__ = 'autorole'
    role_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guildsettings.guild_id"))

    created = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"AutoRole(guild_id={self.guild_id}, "
            f"role_id={self.role_id})"
        )

    def __eq__(self, other: 'AutoRole'):
        return self.role_id == other.role_id and self.guild_id == other.guild_id
