import datetime

from pydantic import BaseModel, ConfigDict


class DuplicateMatch(BaseModel):
    is_duplicate: bool
    matched_user: str | None = None
    matched_filename: str | None = None
    similarity: float | None = None
    uploaded_at: str | None = None


class ModerationResult(BaseModel):
    filename: str
    file_hash: str
    media_type: str
    nsfw_status: str
    nsfw_score: float
    is_nsfw: bool
    frames_analyzed: int = 1
    duplicate: DuplicateMatch
    stored: bool


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_hash: str
    media_type: str
    nsfw_status: str
    nsfw_score: float
    is_nsfw: bool
    uploaded_by: str
    created_at: datetime.datetime
