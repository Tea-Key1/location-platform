# app/schemas/common.py

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class DeleteResponse(BaseModel):
    deleted: bool