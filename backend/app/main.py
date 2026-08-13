from collections import Counter, defaultdict
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from .database import Base, SessionLocal, engine, get_db
from .models import Candidate, CandidateSkill, ProficiencyLevel, Skill, SkillCategory
from .schemas import (
    CandidateDetail,
    CandidateList,
    CandidateSkillOut,
    CandidateSummary,
    CategoryOut,
    ProficiencyOut,
    SkillOut,
)
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(title="PACE Fresher Talent Pool API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def skill_out(item: CandidateSkill) -> CandidateSkillOut:
    return CandidateSkillOut(
        skill_id=item.skill_id,
        skill_name=item.skill.skill_name,
        category_id=item.skill.category_id,
        category_name=item.skill.category.category_name,
        proficiency_id=item.proficiency_id,
        proficiency_name=item.proficiency.level_name,
        proficiency_rank=item.proficiency.level_rank,
    )


def summary(candidate: Candidate, matched_skill_ids: set[int] | None = None) -> CandidateSummary:
    assessed = [item for item in candidate.skills if item.proficiency.level_rank >= 1]
    category_scores: Counter[str] = Counter()
    for item in assessed:
        category_scores[item.skill.category.category_name] += item.proficiency.level_rank
    if not category_scores:
        primary = "Not assessed"
    else:
        highest = max(category_scores.values())
        leaders = [name for name, score in category_scores.items() if score == highest]
        primary = leaders[0] if len(leaders) == 1 else "Cross-domain profile"
    matched = sorted(
        [item for item in assessed if item.skill_id in (matched_skill_ids or set())],
        key=lambda item: (-item.proficiency.level_rank, item.skill.skill_name),
    )
    return CandidateSummary(
        candidate_id=candidate.candidate_id,
        employee_id=candidate.employee_id,
        full_name=candidate.full_name,
        email=candidate.email,
        primary_category=primary,
        matched_skills=[skill_out(item) for item in matched],
        skill_count=len(assessed),
    )


def parse_requirements(raw: list[str]) -> list[tuple[int, int]]:
    requirements = []
    for value in raw:
        try:
            skill_id, rank = (int(part) for part in value.split(":", 1))
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail=f"Invalid skill requirement: {value}")
        if skill_id < 1 or rank not in {1, 2, 3, 4}:
            raise HTTPException(status_code=422, detail=f"Invalid skill requirement: {value}")
        requirements.append((skill_id, rank))
    return requirements


@app.get("/api/v1/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok"}


@app.get("/api/v1/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(SkillCategory).options(selectinload(SkillCategory.skills)).order_by(SkillCategory.display_order)
    ).all()
    return [
        CategoryOut(
            category_id=row.category_id,
            category_name=row.category_name,
            display_order=row.display_order,
            skills=[SkillOut.model_validate(s) for s in sorted(row.skills, key=lambda x: x.skill_name) if s.is_active],
        )
        for row in rows
    ]


@app.get("/api/v1/categories/{category_id}/skills", response_model=list[SkillOut])
def category_skills(category_id: int, db: Session = Depends(get_db)):
    exists = db.get(SkillCategory, category_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Category not found")
    return db.scalars(
        select(Skill).where(Skill.category_id == category_id, Skill.is_active.is_(True)).order_by(Skill.skill_name)
    ).all()


@app.get("/api/v1/proficiency-levels", response_model=list[ProficiencyOut])
def proficiency_levels(db: Session = Depends(get_db)):
    return db.scalars(
        select(ProficiencyLevel)
        .where(ProficiencyLevel.level_rank >= 1)
        .order_by(ProficiencyLevel.level_rank)
    ).all()


@app.get("/api/v1/candidates", response_model=CandidateList)
def candidates(
    q: str | None = Query(None, max_length=100),
    category_id: int | None = None,
    skill: list[str] = Query(default=[]),
    match: str = Query("all", pattern="^(all|any)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    requirements = parse_requirements(skill)
    valid_skills = set(db.scalars(select(Skill.skill_id).where(Skill.skill_id.in_([x[0] for x in requirements])))) if requirements else set()
    if len(valid_skills) != len({x[0] for x in requirements}):
        raise HTTPException(status_code=422, detail="One or more skills do not exist")

    filters = []
    if q and q.strip():
        term = f"%{q.strip().lower()}%"
        filters.append(or_(func.lower(Candidate.full_name).like(term), func.lower(Candidate.employee_id).like(term)))

    if category_id is not None:
        category_match = (
            select(CandidateSkill.candidate_id)
            .join(Skill, Skill.skill_id == CandidateSkill.skill_id)
            .join(ProficiencyLevel, ProficiencyLevel.proficiency_id == CandidateSkill.proficiency_id)
            .where(
                CandidateSkill.candidate_id == Candidate.candidate_id,
                Skill.category_id == category_id,
                ProficiencyLevel.level_rank >= 1,
            )
            .exists()
        )
        filters.append(category_match)

    requirement_filters = []
    for skill_id, minimum_rank in requirements:
        requirement_filters.append(
            select(CandidateSkill.candidate_id)
            .join(ProficiencyLevel, ProficiencyLevel.proficiency_id == CandidateSkill.proficiency_id)
            .where(
                CandidateSkill.candidate_id == Candidate.candidate_id,
                CandidateSkill.skill_id == skill_id,
                ProficiencyLevel.level_rank >= minimum_rank,
            )
            .exists()
        )
    if requirement_filters:
        filters.append(and_(*requirement_filters) if match == "all" else or_(*requirement_filters))

    base = select(Candidate).where(*filters)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(
        base.options(
            selectinload(Candidate.skills).selectinload(CandidateSkill.skill).selectinload(Skill.category),
            selectinload(Candidate.skills).selectinload(CandidateSkill.proficiency),
        )
        .order_by(Candidate.full_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    requirement_ids = {skill_id for skill_id, _ in requirements}
    return CandidateList(
        items=[summary(row, requirement_ids) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@app.get("/api/v1/candidates/{candidate_id}", response_model=CandidateDetail)
def candidate_detail(candidate_id: UUID, db: Session = Depends(get_db)):
    candidate = db.scalar(
        select(Candidate)
        .where(Candidate.candidate_id == candidate_id)
        .options(
            selectinload(Candidate.skills).selectinload(CandidateSkill.skill).selectinload(Skill.category),
            selectinload(Candidate.skills).selectinload(CandidateSkill.proficiency),
        )
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    base = summary(candidate)
    groups: dict[str, list[CandidateSkillOut]] = defaultdict(list)
    for item in sorted(candidate.skills, key=lambda x: (x.skill.category.category_name, -x.proficiency.level_rank)):
        if item.proficiency.level_rank >= 1:
            groups[item.skill.category.category_name].append(skill_out(item))
    top_rank = max((item.proficiency.level_rank for item in candidate.skills), default=0)
    top_level = next(
        (item.proficiency.level_name for item in candidate.skills if item.proficiency.level_rank == top_rank),
        "Not assessed",
    )
    return CandidateDetail(
        **base.model_dump(),
        top_proficiency=top_level,
        category_count=len(groups),
        skills_by_category=dict(groups),
    )
