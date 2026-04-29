from pydantic import BaseModel, Field


class ProgressUpdate(BaseModel):
    position_seconds: int = Field(ge=0)
    completed: bool = False


class ProgressResponse(BaseModel):
    episode_id: int
    position_seconds: int
    completed: bool
