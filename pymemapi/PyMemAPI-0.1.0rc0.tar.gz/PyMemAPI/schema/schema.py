from pydantic import BaseModel, HttpUrl
from typing import List


class Category(BaseModel):
    name: str
    photo: HttpUrl


class Language(BaseModel):
    """Memrise course language."""

    id: int
    slug: str
    name: str
    photo: HttpUrl
    parent_id: int
    index: int
    language_code: str


class CourseSchema(BaseModel):
    """Memrise course schema."""

    id: int
    name: str
    slug: str
    url: str
    description: str
    photo: HttpUrl
    photo_small: HttpUrl
    photo_large: HttpUrl
    num_things: int
    num_levels: int
    num_learners: int
    source: Language
    target: Language
    learned: int
    review: int
    ignored: int
    ltm: int
    difficult: int
    category: Category
    percent_complete: int


class CourseList(BaseModel):
    courses: List[CourseSchema]
    to_review_total: int
    has_more_courses: bool


class EditLevel(BaseModel):
    """Learnable is present for vocabulary"""

    success: bool
    rendered: str


class LevelSchema(BaseModel):
    """Level schema"""

    id: int
    index: int
    kind: int
    title: str
    pool_id: int
    course_id: int
    learnable_ids: List[int]


class LevelList(BaseModel):
    """List of level schema"""

    levels: List[LevelSchema]
    version: str
