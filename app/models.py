"""SQLAlchemy models for the law firm backend."""
from __future__ import annotations

import json
from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base

lawyer_practice_area = Table(
    "lawyer_practice_area",
    Base.metadata,
    Column("lawyer_id", ForeignKey("lawyers.id"), primary_key=True),
    Column("practice_area_id", ForeignKey("practice_areas.id"), primary_key=True),
)


class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    email = Column(String(255), nullable=True, unique=True)
    phone = Column(String(50), nullable=True)
    experience_years = Column(Integer, nullable=True)
    photo_url = Column(String(512), nullable=True)
    _languages = Column("languages", Text, default="[]", nullable=False)

    practice_areas = relationship(
        "PracticeArea",
        secondary=lawyer_practice_area,
        back_populates="lawyers",
        lazy="selectin",
    )
    case_results = relationship(
        "CaseResult", back_populates="lawyer", cascade="all, delete-orphan", lazy="selectin"
    )
    testimonials = relationship(
        "Testimonial", back_populates="lawyer", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def languages(self) -> List[str]:
        try:
            return json.loads(self._languages)
        except json.JSONDecodeError:
            return []

    @languages.setter
    def languages(self, value: List[str]) -> None:
        self._languages = json.dumps(value or [])

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging only
        return f"<Lawyer id={self.id} name={self.full_name!r}>"


class PracticeArea(Base):
    __tablename__ = "practice_areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    lawyers = relationship(
        "Lawyer",
        secondary=lawyer_practice_area,
        back_populates="practice_areas",
        lazy="selectin",
    )
    case_results = relationship(
        "CaseResult", back_populates="practice_area", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging only
        return f"<PracticeArea id={self.id} name={self.name!r}>"


class CaseResult(Base):
    __tablename__ = "case_results"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    resolved_on = Column(Date, nullable=True)

    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), nullable=False)
    practice_area_id = Column(Integer, ForeignKey("practice_areas.id"), nullable=True)

    lawyer = relationship("Lawyer", back_populates="case_results")
    practice_area = relationship("PracticeArea", back_populates="case_results")

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging only
        return f"<CaseResult id={self.id} title={self.title!r}>"


class Testimonial(Base):
    __tablename__ = "testimonials"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)

    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), nullable=False)

    lawyer = relationship("Lawyer", back_populates="testimonials")

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging only
        return f"<Testimonial id={self.id} client={self.client_name!r}>"


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    preferred_contact_method = Column(String(50), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging only
        return f"<ContactMessage id={self.id} email={self.email!r}>"
