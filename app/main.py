"""FastAPI application entry point for the law firm backend."""
from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import get_db, init_db

app = FastAPI(title="Law Firm Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", summary="Genel bilgi")
def root() -> dict[str, str]:
    return {
        "message": "Deniz Hukuk Bürosu API'sine hoş geldiniz.",
        "docs": "/docs",
    }


@app.get("/health", summary="Sağlık durumu")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


# Practice areas ------------------------------------------------------------------


@app.get("/practice-areas", response_model=List[schemas.PracticeAreaRead], summary="Uzmanlık alanlarını listele")
def list_practice_areas(db: Session = Depends(get_db)):
    return crud.list_practice_areas(db)


@app.post(
    "/practice-areas",
    response_model=schemas.PracticeAreaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni uzmanlık alanı oluştur",
)
def create_practice_area(data: schemas.PracticeAreaCreate, db: Session = Depends(get_db)):
    return crud.create_practice_area(db, data)


@app.get(
    "/practice-areas/{practice_area_id}",
    response_model=schemas.PracticeAreaRead,
    summary="Uzmanlık alanı detayı",
)
def get_practice_area(practice_area_id: int, db: Session = Depends(get_db)):
    instance = crud.get_practice_area(db, practice_area_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uzmanlık alanı bulunamadı")
    return instance


@app.put(
    "/practice-areas/{practice_area_id}",
    response_model=schemas.PracticeAreaRead,
    summary="Uzmanlık alanını güncelle",
)
def update_practice_area(
    practice_area_id: int, data: schemas.PracticeAreaUpdate, db: Session = Depends(get_db)
):
    instance = crud.get_practice_area(db, practice_area_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uzmanlık alanı bulunamadı")
    return crud.update_practice_area(db, instance, data)


@app.delete(
    "/practice-areas/{practice_area_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Uzmanlık alanını sil"
)
def delete_practice_area(practice_area_id: int, db: Session = Depends(get_db)):
    instance = crud.get_practice_area(db, practice_area_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uzmanlık alanı bulunamadı")
    crud.delete_practice_area(db, instance)
    return None


# Lawyers -------------------------------------------------------------------------


@app.get(
    "/lawyers",
    response_model=List[schemas.LawyerRead],
    summary="Avukatları listele",
)
def list_lawyers(
    practice_area_id: Optional[int] = Query(None, alias="practiceAreaId"),
    search: Optional[str] = Query(None, description="İsim veya biyografide arama"),
    db: Session = Depends(get_db),
):
    return crud.list_lawyers(db, practice_area_id=practice_area_id, search=search)


@app.post("/lawyers", response_model=schemas.LawyerRead, status_code=status.HTTP_201_CREATED)
def create_lawyer(data: schemas.LawyerCreate, db: Session = Depends(get_db)):
    return crud.create_lawyer(db, data)


@app.get("/lawyers/{lawyer_id}", response_model=schemas.LawyerRead)
def get_lawyer(lawyer_id: int, db: Session = Depends(get_db)):
    instance = crud.get_lawyer(db, lawyer_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avukat bulunamadı")
    return instance


@app.put("/lawyers/{lawyer_id}", response_model=schemas.LawyerRead)
def update_lawyer(lawyer_id: int, data: schemas.LawyerUpdate, db: Session = Depends(get_db)):
    instance = crud.get_lawyer(db, lawyer_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avukat bulunamadı")
    return crud.update_lawyer(db, instance, data)


@app.delete("/lawyers/{lawyer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lawyer(lawyer_id: int, db: Session = Depends(get_db)):
    instance = crud.get_lawyer(db, lawyer_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avukat bulunamadı")
    crud.delete_lawyer(db, instance)
    return None


# Case results --------------------------------------------------------------------


@app.get("/case-results", response_model=List[schemas.CaseResultRead])
def list_case_results(db: Session = Depends(get_db)):
    results = crud.list_case_results(db)
    return [
        schemas.CaseResultRead.from_orm(result).copy(
            update={
                "lawyer_name": result.lawyer.full_name if result.lawyer else None,
                "practice_area_name": result.practice_area.name if result.practice_area else None,
            }
        )
        for result in results
    ]


@app.post("/case-results", response_model=schemas.CaseResultRead, status_code=status.HTTP_201_CREATED)
def create_case_result(data: schemas.CaseResultCreate, db: Session = Depends(get_db)):
    result = crud.create_case_result(db, data)
    db.refresh(result)
    return schemas.CaseResultRead.from_orm(result).copy(
        update={
            "lawyer_name": result.lawyer.full_name if result.lawyer else None,
            "practice_area_name": result.practice_area.name if result.practice_area else None,
        }
    )


@app.get("/case-results/{case_result_id}", response_model=schemas.CaseResultRead)
def get_case_result(case_result_id: int, db: Session = Depends(get_db)):
    result = crud.get_case_result(db, case_result_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Başarı hikayesi bulunamadı")
    return schemas.CaseResultRead.from_orm(result).copy(
        update={
            "lawyer_name": result.lawyer.full_name if result.lawyer else None,
            "practice_area_name": result.practice_area.name if result.practice_area else None,
        }
    )


@app.put("/case-results/{case_result_id}", response_model=schemas.CaseResultRead)
def update_case_result(case_result_id: int, data: schemas.CaseResultUpdate, db: Session = Depends(get_db)):
    instance = crud.get_case_result(db, case_result_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Başarı hikayesi bulunamadı")
    result = crud.update_case_result(db, instance, data)
    db.refresh(result)
    return schemas.CaseResultRead.from_orm(result).copy(
        update={
            "lawyer_name": result.lawyer.full_name if result.lawyer else None,
            "practice_area_name": result.practice_area.name if result.practice_area else None,
        }
    )


@app.delete("/case-results/{case_result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case_result(case_result_id: int, db: Session = Depends(get_db)):
    instance = crud.get_case_result(db, case_result_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Başarı hikayesi bulunamadı")
    crud.delete_case_result(db, instance)
    return None


# Testimonials --------------------------------------------------------------------


@app.get("/testimonials", response_model=List[schemas.TestimonialRead])
def list_testimonials(db: Session = Depends(get_db)):
    testimonials = crud.list_testimonials(db)
    return [
        schemas.TestimonialRead.from_orm(item).copy(update={"lawyer_name": item.lawyer.full_name})
        for item in testimonials
    ]


@app.post("/testimonials", response_model=schemas.TestimonialRead, status_code=status.HTTP_201_CREATED)
def create_testimonial(data: schemas.TestimonialCreate, db: Session = Depends(get_db)):
    testimonial = crud.create_testimonial(db, data)
    db.refresh(testimonial)
    return schemas.TestimonialRead.from_orm(testimonial).copy(
        update={"lawyer_name": testimonial.lawyer.full_name if testimonial.lawyer else None}
    )


@app.get("/testimonials/{testimonial_id}", response_model=schemas.TestimonialRead)
def get_testimonial(testimonial_id: int, db: Session = Depends(get_db)):
    testimonial = crud.get_testimonial(db, testimonial_id)
    if not testimonial:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geri bildirim bulunamadı")
    return schemas.TestimonialRead.from_orm(testimonial).copy(
        update={"lawyer_name": testimonial.lawyer.full_name if testimonial.lawyer else None}
    )


@app.put("/testimonials/{testimonial_id}", response_model=schemas.TestimonialRead)
def update_testimonial(testimonial_id: int, data: schemas.TestimonialUpdate, db: Session = Depends(get_db)):
    instance = crud.get_testimonial(db, testimonial_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geri bildirim bulunamadı")
    testimonial = crud.update_testimonial(db, instance, data)
    db.refresh(testimonial)
    return schemas.TestimonialRead.from_orm(testimonial).copy(
        update={"lawyer_name": testimonial.lawyer.full_name if testimonial.lawyer else None}
    )


@app.delete("/testimonials/{testimonial_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_testimonial(testimonial_id: int, db: Session = Depends(get_db)):
    instance = crud.get_testimonial(db, testimonial_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geri bildirim bulunamadı")
    crud.delete_testimonial(db, instance)
    return None


# Contact messages ----------------------------------------------------------------


@app.get("/contact-messages", response_model=List[schemas.ContactMessageRead])
def list_contact_messages(db: Session = Depends(get_db)):
    return crud.list_contact_messages(db)


@app.post(
    "/contact-messages",
    response_model=schemas.ContactMessageRead,
    status_code=status.HTTP_201_CREATED,
)
def create_contact_message(data: schemas.ContactMessageCreate, db: Session = Depends(get_db)):
    message = crud.create_contact_message(db, data)
    db.refresh(message)
    return message
