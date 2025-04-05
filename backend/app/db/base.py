import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True if settings.DEBUG else False,
)

# Create sessionmaker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base model
Base = declarative_base()

# Dependency to get async DB session
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

class BaseModel(Base):
    """Base model for all SQLAlchemy models"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 