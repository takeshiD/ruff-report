from enum import Enum

from pydantic import BaseModel, Field, PositiveInt, RootModel


class Location(BaseModel):
    column: PositiveInt = Field(...)
    row: PositiveInt = Field(...)


class Edit(BaseModel):
    content: str | None = Field(default=None)
    location: Location = Field(...)
    end_location: Location = Field(...)


class Applicability(str, Enum):
    DisplayOnly = "displayonly"
    Unsafe = "unsafe"
    Safe = "safe"


class Fix(BaseModel):
    edits: list[Edit]
    applicability: Applicability
    message: str


class Violation(BaseModel):
    cell: str | None = Field(default=None)
    code: str | None = Field(default=None)
    location: Location = Field(...)
    end_location: Location | None = Field(...)
    filename: str = Field(...)
    message: str = Field(...)
    noqa_row: PositiveInt | None = Field(default=None)
    url: str | None = Field(default=None)
    fix: Fix | None = Field(default=None)

ViolationList = RootModel[list[Violation]]

class RuffReport(BaseModel):
    timestamp: str = Field(...)
    branch_name: str = Field(...)
    commit_hash: str = Field(...)
    violations: ViolationList
