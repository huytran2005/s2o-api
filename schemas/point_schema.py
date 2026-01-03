from pydantic import BaseModel

class PointResponse(BaseModel):
    total_points: int
