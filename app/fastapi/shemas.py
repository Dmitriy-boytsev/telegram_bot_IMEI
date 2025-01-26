from pydantic import BaseModel, Field
from typing import Optional, Dict


class IMEICheckRequest(BaseModel):
    imei: str
    serviceid: int = Field(..., description="Service ID must be an integer")


class IMEICheckResponse(BaseModel):
    details: Optional[Dict]


class UserWhitelistRequest(BaseModel):
    telegram_id: int
    username: str = None