from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float, CheckConstraint, Boolean
from datetime import datetime

Base = declarative_base(cls=AsyncAttrs)


class MemberDB(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, default="")

    referrer_id = Column(
        Integer,
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True
    )

    referrer = relationship(
        "MemberDB",
        remote_side=[id],  # <--- исправлено
        foreign_keys=[referrer_id],
        back_populates="team",
        lazy="selectin"
    )

    team = relationship(
        "MemberDB",
        back_populates="referrer",
        foreign_keys=[referrer_id],
        lazy="selectin"
    )

    stats = relationship(
        "MemberStatsDB",
        uselist=False,
        back_populates="member",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class MemberStatsDB(Base):
    __tablename__ = "member_stats"

    member_id = Column(
        Integer,
        ForeignKey("members.id", ondelete="CASCADE"),
        primary_key=True
    )

    lo = Column(Float, default=0, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    last_active = Column(DateTime, nullable=True)

    period_start = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    member = relationship(
        "MemberDB",
        back_populates="stats",
        lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("lo >= 0", name="ck_member_stats_lo_non_negative"),
    )


class MemberStatsHistoryDB(Base):
    __tablename__ = "member_stats_history"

    id = Column(Integer, primary_key=True)

    member_id = Column(
        Integer,
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    lo = Column(Float, nullable=False)
    qualification = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
