from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Sport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    athletes: List["Athlete"] = Relationship(back_populates="sport")


class Athlete(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    sport_id: Optional[int] = Field(default=None, foreign_key="sport.id")
    sport: Optional[Sport] = Relationship(back_populates="athletes")
