from datetime import datetime
from uuid import UUID

import pyjq
from pydantic import BaseModel, HttpUrl
from pydantic.class_validators import validator

from universal_webhooks.settings import settings


class JQQuery(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            examples=[".something", "[{foo: .bar}]"],
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")

        if not v:
            raise ValueError("string must not be empty")

        pyjq.compile(v)

        return cls(v)

    def __repr__(self):
        return f"JQQuery({super().__repr__()})"


class AdapterBase(BaseModel):
    send_to: HttpUrl
    translation_query: JQQuery

    @validator("send_to")
    def send_to_no_recursion(cls, v):
        if settings.host_url in v:
            raise ValueError(
                "destination address must not be this application's address"
            )
        return v


class AdapterCreate(AdapterBase):
    pass


class Adapter(AdapterBase):
    id: UUID
    last_access: datetime

    class Config:
        orm_mode = True
