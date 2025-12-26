from uuid import UUID
from pydantic import BaseModel, ConfigDict

class RestaurantCreate(BaseModel):
    name: str
    description: str | None = None


class RestaurantUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class RestaurantResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    image_preview: str | None

    model_config = ConfigDict(from_attributes=True)
