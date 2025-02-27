import logging
import time
from typing import Optional

from open_webui.internal.db import Base, get_db
from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel
from sqlalchemy import BigInteger, Column, String, Text, JSON

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Companies DB Schema
####################

class Company(Base):
    __tablename__ = "company"
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    nicknames = Column(JSON, nullable=True)
    description = Column(Text)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)

class CompanyModel(BaseModel):
    id: str
    name: str
    nicknames: Optional[list[str]] = None
    description: str
    created_at: int
    updated_at: int

    def __str__(self) -> str:
        return f"{self.name}[[company:{self.id}]]"

    @classmethod
    def model_validate(cls, company: Company) -> "CompanyModel":
        """
        SQLAlchemy의 Company 객체를 Pydantic CompanyModel로 변환할 때,
        nicknames 필드의 타입을 안전하게 변환
        """
        return cls(
            id=company.id,
            name=company.name,
            nicknames=company.nicknames if isinstance(company.nicknames, list) else [],
            description=company.description,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )

class CompanyForm(BaseModel):
    id: str
    name: str
    nicknames: Optional[list[str]] = None
    description: str

class CompanyTable:
    def insert_new_company(self, form_data: CompanyForm) -> Optional[CompanyModel]:
        with get_db() as db:
            company = CompanyModel(
                **{
                    **form_data.model_dump(),
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            return company

    def get_company_by_id(self, id: str) -> Optional[CompanyModel]:
        with get_db() as db:
            return db.query(Company).filter(Company.id == id).first()

    def get_companies(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> list[CompanyModel]:
        try:
            with get_db() as db:
                query = db.query(Company).order_by(Company.created_at.desc())

                if skip:
                    query = query.offset(skip)
                if limit:
                    query = query.limit(limit)

                companies = query.all()

                return [CompanyModel.model_validate(company) for company in companies]
        except Exception as e:
            log.info(f"get_companies... error: {e}")
            return []
        
    def update_company_by_id(self, id: str, form_data: CompanyForm) -> Optional[CompanyModel]:
        with get_db() as db:
            company = db.query(Company).filter(Company.id == id).first()
            if company:
                company.name = form_data.name
                company.nicknames = form_data.nicknames
                company.description = form_data.description
                company.updated_at = int(time.time())
                db.commit()
                db.refresh(company)
                return company
            return None
        
    def delete_company_by_id(self, id: str) -> bool:
        with get_db() as db:
            company = db.query(Company).filter(Company.id == id).first()
            if company:
                db.delete(company)
                db.commit()
                return True
            return False
        
    def delete_all_companies(self) -> bool:
        with get_db() as db:
            db.query(Company).delete()
            db.commit()
            return True

    def get_company_by_name(self, name: str) -> Optional[CompanyModel]:
        with get_db() as db:
            return db.query(Company).filter(Company.name == name).first()
        
    def get_company_by_nickname(self, nickname: str) -> Optional[CompanyModel]:
        with get_db() as db:
            return db.query(Company).filter(Company.nicknames.contains(nickname)).first()
        

Companies = CompanyTable()
