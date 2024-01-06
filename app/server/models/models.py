import uuid
from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, UUID4, validator


def validate_uuid(string: str):
    uuid.UUID(string)


class EventModel(BaseModel):
    id: UUID4
    name: str
    date: datetime
    location: str
    creation_date: Optional[datetime]
    participants_num: Optional[int]

    class Config:
        orm_mode = True


class EventCreateRequest(BaseModel):
    name: str
    date: datetime
    location: str
    creation_date: Optional[datetime]
    participants_num: Optional[int]


class CreateEventsRequest(BaseModel):
    events: List[EventCreateRequest]


class EventDeleteRequest(BaseModel):
    events: Optional[List[str]]

    @validator("events")
    def validate_event(cls, value):
        for e in value:
            validate_uuid(e)
        return value


class AdminEventDeleteRequest(EventDeleteRequest):
    permanent: bool = False


class SingleEventUpdateRequest(BaseModel):
    name: Optional[str]
    date: Optional[datetime]
    location: Optional[str]
    creation_date: Optional[datetime]
    participants_num: Optional[int]
    deleted: Optional[bool]


class EventUpdate(SingleEventUpdateRequest):
    id: str

    @validator("id")
    def validate_id(cls, value):
        validate_uuid(value)
        return value


class EventUpdateRequest(BaseModel):
    updates: List[EventUpdate]


class GetEventsRequest(BaseModel):
    name: Optional[str]
    location: Optional[str]
    participants_num: Optional[int]
    sort_by: Optional[Literal['date','participants_num','creation_date']]
