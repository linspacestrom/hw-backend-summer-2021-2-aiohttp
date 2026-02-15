from dataclasses import dataclass


@dataclass
class Theme:
    id: int | None
    title: str


@dataclass
class Question:
    id: int
    title: str
    theme_id: int
    answers: list["Answer"]


@dataclass
class Answer:
    title: str
    is_correct: bool
