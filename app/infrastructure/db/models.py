from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, Float, ForeignKey, String, CheckConstraint

Base = declarative_base(cls=AsyncAttrs)

class MemberDB(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, unique=True, nullable=False, index=True)

    name = Column(String, nullable=True, default="")

    referrer_id = Column(
        Integer,
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True
    )

    lo = Column(Float, default=0)

    referrer = relationship(
        "MemberDB",
        remote_side=[id],
        back_populates="team",
        lazy="selectin"
    )

    team = relationship(
        "MemberDB",
        back_populates="referrer",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # __table_args__ = (
    #     CheckConstraint("lo >= 0", name="ck_member_lo_non_negative"),
    # )

