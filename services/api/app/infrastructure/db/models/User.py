from sqlalchemy.engine import default
import uuid
import enum
from sqlalchemy import Boolean, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column                                                                                                                                      
from app.infrastructure.db.models.base import Base  

class UserRole(str, enum.Enum):
    CTO = "CTO"
    PM = "PM"
    DEV = "DEV"

class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role : Mapped[UserRole] = mapped_column(
      SQLEnum(UserRole),
      default=UserRole.DEV,
      nullable=False,
    )