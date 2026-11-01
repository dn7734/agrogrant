import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, String, Table, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.getenv("postgresql://neondb_owner:npg_HgPn1QCceUF9@ep-old-smoke-ba9yav8w.c-8.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
engine = create_engine("postgresql://neondb_owner:npg_HgPn1QCceUF9@ep-old-smoke-ba9yav8w.c-8.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    agreed_to_privacy = Column(String, default="false")
    profile = relationship("EnterpriseProfile", back_populates="user")


class EnterpriseProfile(Base):
    __tablename__ = "enterprise_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    region = Column(String, nullable=True)
    activity_type = Column(String, nullable=True)
    size_category = Column(String, nullable=True)
    employees_count = Column(String, nullable=True)
    investment_focus = Column(String, nullable=True)
    own_contribution_percent = Column(String, nullable=True)
    user = relationship("User", back_populates="profile")


Base.metadata.create_all(bind=engine)

app = FastAPI()


class UserCreate(BaseModel):
    session_id: str


class ProfileUpdate(BaseModel):
    region: Optional[str] = None
    activity_type: Optional[str] = None
    size_category: Optional[str] = None
    employees_count: Optional[str] = None
    investment_focus: Optional[str] = None
    own_contribution_percent: Optional[str] = None


@app.post("/users/")
def create_user(user: UserCreate):
    db = SessionLocal()
    db_user = User(session_id=user.session_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return {"user_id": db_user.id}


@app.post("/profiles/{user_id}")
def update_profile(user_id: uuid.UUID, profile_data: ProfileUpdate):
    db = SessionLocal()
    db_profile = (
        db.query(EnterpriseProfile)
        .filter(EnterpriseProfile.user_id == user_id)
        .first()
    )
    if not db_profile:
        db_profile = EnterpriseProfile(
            user_id=user_id, **profile_data.dict(exclude_unset=True)
        )
        db.add(db_profile)
    else:
        for key, value in profile_data.dict(exclude_unset=True).items():
            setattr(db_profile, key, value)
    db.commit()
    db.refresh(db_profile)
    db.close()
    return {"profile_id": db_profile.id}

