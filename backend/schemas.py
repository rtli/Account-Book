from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# ========== Category Schemas ==========
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    parent_id: Optional[int] = None
    level: int = Field(default=2, ge=1, le=2)


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    level: int

    class Config:
        from_attributes = True


class CategoryTree(BaseModel):
    id: int
    name: str
    level: int
    children: list["CategoryTree"] = []

    class Config:
        from_attributes = True


# ========== Spending Schemas ==========
class SpendingCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=100)
    category_id: int
    amount: float = Field(..., gt=0)
    spend_date: Optional[date] = None


class SpendingUpdate(BaseModel):
    item_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    spend_date: Optional[date] = None


class SpendingResponse(BaseModel):
    id: int
    item_name: str
    category_id: int
    category_name: str = ""
    amount: float
    spend_date: date
    created_at: str = ""

    class Config:
        from_attributes = True


class SpendingListResponse(BaseModel):
    items: list[SpendingResponse]
    total: int
    page: int
    page_size: int


# ========== Statistics Schemas ==========
class SankeyNode(BaseModel):
    name: str


class SankeyLink(BaseModel):
    source: str
    target: str
    value: float


class SankeyResponse(BaseModel):
    nodes: list[SankeyNode]
    links: list[SankeyLink]


class MonthlySummary(BaseModel):
    month: str
    total: float


class CategorySummary(BaseModel):
    name: str
    total: float
