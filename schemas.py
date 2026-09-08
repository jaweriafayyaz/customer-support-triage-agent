from typing import Optional, Literal
from pydantic import BaseModel, Field

Category = Literal["Billing", "Refund", "Shipping", "Technical", "General", "Unroutable"]
Action = Literal["auto_approved", "needs_human_review"]


class Ticket(BaseModel):
    ticket_id: str
    subject: str
    body: str


class ClassificationResult(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)


class TicketResult(BaseModel):
    ticket_id: str
    category: Category
    confidence: float
    retrieved_context: Optional[str] = None
    draft_reply: str
    action: Action
    flagged_reason: Optional[str] = None