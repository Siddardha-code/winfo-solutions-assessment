from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    billing = "billing"
    technical = "technical"
    account = "account"
    feature_request = "feature_request"
    general = "general"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TicketIn(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)
    customer_name: str | None = Field(default=None, max_length=100)


class Triage(BaseModel):
    category: Category
    priority: Priority
    summary: str = Field(max_length=500)
    suggested_response: str = Field(max_length=2000)


class TicketOut(Triage):
    request_id: str
    model_id: str
