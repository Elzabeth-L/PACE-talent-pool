from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProficiencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    proficiency_id: int
    level_name: str
    level_rank: int


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: int
    category_id: int
    skill_name: str


class CategoryOut(BaseModel):
    category_id: int
    category_name: str
    display_order: int
    skills: list[SkillOut] = []


class CandidateSkillOut(BaseModel):
    skill_id: int
    skill_name: str
    category_id: int
    category_name: str
    proficiency_id: int
    proficiency_name: str
    proficiency_rank: int


class CandidateSummary(BaseModel):
    candidate_id: UUID
    employee_id: str
    full_name: str
    email: str
    primary_category: str
    matched_skills: list[CandidateSkillOut] = []
    skill_count: int


class CandidateDetail(CandidateSummary):
    top_proficiency: str
    category_count: int
    skills_by_category: dict[str, list[CandidateSkillOut]]


class CandidateList(BaseModel):
    items: list[CandidateSummary]
    total: int
    page: int
    page_size: int
