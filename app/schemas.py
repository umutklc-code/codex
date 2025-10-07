"""Pydantic schemas for request and response models."""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class PracticeAreaBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class PracticeAreaCreate(PracticeAreaBase):
    pass


class PracticeAreaUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class PracticeAreaRead(PracticeAreaBase):
    id: int

    class Config:
        orm_mode = True


class LawyerBase(BaseModel):
    full_name: str = Field(..., max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    experience_years: Optional[int] = Field(None, ge=0)
    photo_url: Optional[str] = Field(None, max_length=512)
    languages: List[str] = []
    practice_area_ids: List[int] = []

    @validator("languages", pre=True)
    def validate_languages(cls, value):  # type: ignore[override]
        if isinstance(value, str):
            return [value]
        return value


class LawyerCreate(LawyerBase):
    pass


class LawyerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    experience_years: Optional[int] = Field(None, ge=0)
    photo_url: Optional[str] = Field(None, max_length=512)
    languages: Optional[List[str]] = None
    practice_area_ids: Optional[List[int]] = None

    @validator("languages", pre=True)
    def validate_languages(cls, value):  # type: ignore[override]
        if value is None:
            return value
        if isinstance(value, str):
            return [value]
        return value


class LawyerRead(BaseModel):
    id: int
    full_name: str
    title: Optional[str]
    bio: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    experience_years: Optional[int]
    photo_url: Optional[str]
    languages: List[str] = []
    practice_areas: List[PracticeAreaRead] = []

    class Config:
        orm_mode = True


class CaseResultBase(BaseModel):
    title: str = Field(..., max_length=255)
    summary: Optional[str] = None
    outcome: Optional[str] = None
    resolved_on: Optional[date] = None
    lawyer_id: int
    practice_area_id: Optional[int] = None


class CaseResultCreate(CaseResultBase):
    pass


class CaseResultUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    outcome: Optional[str] = None
    resolved_on: Optional[date] = None
    lawyer_id: Optional[int] = None
    practice_area_id: Optional[int] = None


class CaseResultRead(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    outcome: Optional[str]
    resolved_on: Optional[date]
    lawyer_id: int
    practice_area_id: Optional[int]
    lawyer_name: Optional[str] = None
    practice_area_name: Optional[str] = None

    class Config:
        orm_mode = True


class TestimonialBase(BaseModel):
    client_name: str = Field(..., max_length=255)
    content: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    lawyer_id: int


class TestimonialCreate(TestimonialBase):
    pass


class TestimonialUpdate(BaseModel):
    client_name: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    lawyer_id: Optional[int] = None


class TestimonialRead(BaseModel):
    id: int
    client_name: str
    content: str
    rating: Optional[int]
    lawyer_id: int
    lawyer_name: Optional[str] = None

    class Config:
        orm_mode = True


class ContactMessageCreate(BaseModel):
    full_name: str = Field(..., max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    preferred_contact_method: Optional[str] = Field(None, max_length=50)
    message: str


class ContactMessageRead(ContactMessageCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
