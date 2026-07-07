from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class ProfileUpdate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: Optional[str] = None

class CarbonHistoryEntry(BaseModel):
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$") # YYYY-MM
    transport: float = Field(..., ge=0)
    electricity: float = Field(..., ge=0)
    water: float = Field(..., ge=0)
    food: float = Field(..., ge=0)
    waste: float = Field(..., ge=0)

class GoalCreate(BaseModel):
    category: str = Field(..., min_length=2)
    target_value: float = Field(..., gt=0)
    deadline: str = Field(..., pattern=r"^\d{4}-\d{2}$") # YYYY-MM

class GoalUpdateStatus(BaseModel):
    status: str # "Active", "Achieved", "Failed"

class OffsetBuy(BaseModel):
    offset_id: int
    quantity: int = Field(..., gt=0)

class PostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    content: str = Field(..., min_length=5)

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)

class ChatPrompt(BaseModel):
    message: str
