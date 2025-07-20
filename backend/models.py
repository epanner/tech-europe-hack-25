from typing import List
from enum import Enum
from pydantic import BaseModel, Field

class Classification(str, Enum):
    """
    Represents the possible classifications for GDPR paragraphs.
    Using str as a base ensures the enum values are strings.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class GdprParagraph(BaseModel):
    """
    Represents a single paragraph of the GDPR, including its name,
    classification, and the reason for its classification.
    """
    name: str = Field(..., description="The name or identifier of the GDPR paragraph (e.g., 'Article 6').")
    description: str = Field(..., description="A short description of the paragraph.")
    classification: Classification = Field(..., description="The classification of the GDPR paragraph (e.g., 'Lawful Basis', 'Data Subject Rights').")
    summary: str = Field(..., description="A summary of the paragraph")
    reason: str = Field(..., description="The reason or justification for the given classification.")

class GdprParagraphList(BaseModel):
    """
    Represents a list of GDPR paragraphs. This model can be used when
    expecting a collection of GdprParagraph objects, for example,
    as a response from an API or for validation of a JSON array.
    """
    paragraphs: List[GdprParagraph] = Field(..., description="A list of GDPR paragraph objects.")

class CaseDescription(BaseModel):
    is_case_description: bool
    reasoning: str