from typing import Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class VoteResponse(BaseModel):
    """Response for voting operations"""
    success: bool
    message: str
    votes: int

    model_config = ConfigDict(from_attributes=True)
