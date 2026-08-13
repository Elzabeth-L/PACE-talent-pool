import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Candidate(Base):
    __tablename__ = "candidate"

    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    skills: Mapped[list["CandidateSkill"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan", lazy="selectin"
    )


class SkillCategory(Base):
    __tablename__ = "skill_category"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    skills: Mapped[list["Skill"]] = relationship(back_populates="category", lazy="selectin")


class Skill(Base):
    __tablename__ = "skill"

    skill_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("skill_category.category_id"), nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    category: Mapped[SkillCategory] = relationship(back_populates="skills")
    candidates: Mapped[list["CandidateSkill"]] = relationship(back_populates="skill")


class ProficiencyLevel(Base):
    __tablename__ = "proficiency_level"

    proficiency_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level_name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    level_rank: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    candidate_skills: Mapped[list["CandidateSkill"]] = relationship(back_populates="proficiency")


class CandidateSkill(Base):
    __tablename__ = "candidate_skill"
    __table_args__ = (
        UniqueConstraint("candidate_id", "skill_id"),
        Index("ix_candidate_skill_filter", "skill_id", "proficiency_id", "candidate_id"),
    )

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate.candidate_id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.skill_id"), primary_key=True)
    proficiency_id: Mapped[int] = mapped_column(ForeignKey("proficiency_level.proficiency_id"), nullable=False)
    candidate: Mapped[Candidate] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship(back_populates="candidates", lazy="joined")
    proficiency: Mapped[ProficiencyLevel] = relationship(back_populates="candidate_skills", lazy="joined")
