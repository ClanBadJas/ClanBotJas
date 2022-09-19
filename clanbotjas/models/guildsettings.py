from datetime import datetime

from sqlalchemy import Column, DateTime, BigInteger, String
from sqlalchemy.orm import relationship

from .base import Base


class GuildSettings(Base):
    __tablename__ = 'guildsettings'

    guild_id = Column(BigInteger, primary_key=True)
    log_channel_id = Column(BigInteger, nullable=True)
    privileged_command_role_id = Column(BigInteger, nullable=True)
    voice_scalar_category_id = Column(BigInteger, nullable=True)
    voice_scalar_default_name = Column(String(30), nullable=True)
    rolebot_settings_channel_id = Column(BigInteger, nullable=True)
    autoroles = relationship("AutoRole", backref="guildsettings", lazy='joined')

    created = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"GuildSettings(guild_id={self.guild_id}, "
            f"log_channel_id={self.log_channel_id})"
        )
