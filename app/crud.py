"""Database interaction helpers for the law firm backend."""
from __future__ import annotations

from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import models, schemas


# Practice areas -----------------------------------------------------------------

def list_practice_areas(db: Session) -> List[models.PracticeArea]:
    return db.execute(select(models.PracticeArea).order_by(models.PracticeArea.name)).scalars().all()


def get_practice_area(db: Session, practice_area_id: int) -> Optional[models.PracticeArea]:
    return db.get(models.PracticeArea, practice_area_id)


def create_practice_area(db: Session, data: schemas.PracticeAreaCreate) -> models.PracticeArea:
    practice_area = models.PracticeArea(**data.dict())
    db.add(practice_area)
    db.flush()
    return practice_area


def update_practice_area(
    db: Session, instance: models.PracticeArea, data: schemas.PracticeAreaUpdate
) -> models.PracticeArea:
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(instance, key, value)
    db.add(instance)
    db.flush()
    return instance


def delete_practice_area(db: Session, instance: models.PracticeArea) -> None:
    db.delete(instance)
    db.flush()


# Lawyer helpers ------------------------------------------------------------------

def list_lawyers(
    db: Session,
    *,
    practice_area_id: Optional[int] = None,
    search: Optional[str] = None,
) -> Sequence[models.Lawyer]:
    stmt = select(models.Lawyer).options(selectinload(models.Lawyer.practice_areas))

    if practice_area_id is not None:
        stmt = stmt.join(models.Lawyer.practice_areas).where(models.PracticeArea.id == practice_area_id)
    if search:
        search_term = f"%{search.lower()}%"
        stmt = stmt.where(models.Lawyer.full_name.ilike(search_term) | models.Lawyer.bio.ilike(search_term))

    stmt = stmt.order_by(models.Lawyer.full_name)
    return db.execute(stmt).scalars().unique().all()


def get_lawyer(db: Session, lawyer_id: int) -> Optional[models.Lawyer]:
    stmt = (
        select(models.Lawyer)
        .options(
            selectinload(models.Lawyer.practice_areas),
            selectinload(models.Lawyer.case_results),
            selectinload(models.Lawyer.testimonials),
        )
        .where(models.Lawyer.id == lawyer_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def _attach_practice_areas(
    db: Session, lawyer: models.Lawyer, practice_area_ids: Optional[List[int]]
) -> None:
    if practice_area_ids is None:
        return
    if not practice_area_ids:
        lawyer.practice_areas.clear()
        return

    areas = (
        db.execute(
            select(models.PracticeArea).where(models.PracticeArea.id.in_(practice_area_ids))
        )
        .scalars()
        .all()
    )
    lawyer.practice_areas = areas


def create_lawyer(db: Session, data: schemas.LawyerCreate) -> models.Lawyer:
    lawyer = models.Lawyer(
        full_name=data.full_name,
        title=data.title,
        bio=data.bio,
        email=data.email,
        phone=data.phone,
        experience_years=data.experience_years,
        photo_url=data.photo_url,
    )
    lawyer.languages = data.languages
    _attach_practice_areas(db, lawyer, data.practice_area_ids)
    db.add(lawyer)
    db.flush()
    return lawyer


def update_lawyer(db: Session, instance: models.Lawyer, data: schemas.LawyerUpdate) -> models.Lawyer:
    update_data = data.dict(exclude_unset=True)
    languages = update_data.pop("languages", None)
    practice_area_ids = update_data.pop("practice_area_ids", None)

    for key, value in update_data.items():
        setattr(instance, key, value)

    if languages is not None:
        instance.languages = languages
    if practice_area_ids is not None:
        _attach_practice_areas(db, instance, practice_area_ids)

    db.add(instance)
    db.flush()
    return instance


def delete_lawyer(db: Session, instance: models.Lawyer) -> None:
    db.delete(instance)
    db.flush()


# Case results --------------------------------------------------------------------

def list_case_results(db: Session) -> Sequence[models.CaseResult]:
    stmt = (
        select(models.CaseResult)
        .options(selectinload(models.CaseResult.lawyer), selectinload(models.CaseResult.practice_area))
        .order_by(models.CaseResult.resolved_on.desc().nullslast(), models.CaseResult.title)
    )
    return db.execute(stmt).scalars().all()


def get_case_result(db: Session, case_result_id: int) -> Optional[models.CaseResult]:
    stmt = (
        select(models.CaseResult)
        .options(selectinload(models.CaseResult.lawyer), selectinload(models.CaseResult.practice_area))
        .where(models.CaseResult.id == case_result_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def create_case_result(db: Session, data: schemas.CaseResultCreate) -> models.CaseResult:
    case_result = models.CaseResult(**data.dict())
    db.add(case_result)
    db.flush()
    return case_result


def update_case_result(
    db: Session, instance: models.CaseResult, data: schemas.CaseResultUpdate
) -> models.CaseResult:
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(instance, key, value)
    db.add(instance)
    db.flush()
    return instance


def delete_case_result(db: Session, instance: models.CaseResult) -> None:
    db.delete(instance)
    db.flush()


# Testimonials --------------------------------------------------------------------

def list_testimonials(db: Session) -> Sequence[models.Testimonial]:
    stmt = select(models.Testimonial).options(selectinload(models.Testimonial.lawyer)).order_by(
        models.Testimonial.id.desc()
    )
    return db.execute(stmt).scalars().all()


def get_testimonial(db: Session, testimonial_id: int) -> Optional[models.Testimonial]:
    stmt = (
        select(models.Testimonial)
        .options(selectinload(models.Testimonial.lawyer))
        .where(models.Testimonial.id == testimonial_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def create_testimonial(db: Session, data: schemas.TestimonialCreate) -> models.Testimonial:
    testimonial = models.Testimonial(**data.dict())
    db.add(testimonial)
    db.flush()
    return testimonial


def update_testimonial(
    db: Session, instance: models.Testimonial, data: schemas.TestimonialUpdate
) -> models.Testimonial:
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(instance, key, value)
    db.add(instance)
    db.flush()
    return instance


def delete_testimonial(db: Session, instance: models.Testimonial) -> None:
    db.delete(instance)
    db.flush()


# Contact messages ----------------------------------------------------------------

def list_contact_messages(db: Session) -> Sequence[models.ContactMessage]:
    stmt = select(models.ContactMessage).order_by(models.ContactMessage.created_at.desc())
    return db.execute(stmt).scalars().all()


def create_contact_message(db: Session, data: schemas.ContactMessageCreate) -> models.ContactMessage:
    message = models.ContactMessage(**data.dict())
    db.add(message)
    db.flush()
    return message
