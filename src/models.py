"""Data models for the Fact-Checking Web App."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class VerificationStatus(Enum):
    """Status of a claim verification."""
    VERIFIED = "Verified"
    INACCURATE = "Inaccurate"
    FALSE = "False"
    PENDING = "Pending"


@dataclass
class Claim:
    """Represents a single claim extracted from a document."""
    text: str
    context: str
    page_number: int
    claim_type: str = ""  # e.g., "statistic", "date", "financial", "technical"
    

@dataclass
class Source:
    """A source used for verification."""
    title: str
    url: str
    snippet: str


@dataclass
class VerificationResult:
    """Result of verifying a claim."""
    claim: Claim
    status: VerificationStatus
    explanation: str
    correct_info: Optional[str] = None
    sources: List[Source] = field(default_factory=list)
    confidence: float = 0.0
