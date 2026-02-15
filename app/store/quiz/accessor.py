from app.base.base_accessor import BaseAccessor
from app.quiz.models import Answer, Question, Theme
from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        if await self.get_theme_by_title(title) is not None:
            raise HTTPConflict

        theme = Theme(id=self.app.database.next_theme_id, title=title)
        self.app.database.themes.append(theme)
        return theme

    async def get_theme_by_title(self, title: str) -> Theme | None:
        for theme in self.app.database.themes:
            if theme.title == title:
                return theme
        return None

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        for theme in self.app.database.themes:
            if theme.id == id_:
                return theme
        return None

    async def list_themes(self) -> list[Theme]:
        return self.app.database.themes

    async def get_question_by_title(self, title: str) -> Question | None:
        for question in self.app.database.questions:
            if question.title == title:
                return question
        return None

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        if await self.get_theme_by_id(theme_id) is None:
            raise HTTPNotFound

        if await self.get_question_by_title(title) is not None:
            raise HTTPConflict

        if len(answers) <= 1:
            raise HTTPBadRequest

        count_correct_answer = len([answer for answer in answers if answer.is_correct])
        if count_correct_answer == 0 or count_correct_answer > 1:
            raise HTTPBadRequest

        new_question = Question(id = len(self.app.database.questions)+1, title=title, theme_id=theme_id, answers=answers)
        self.app.database.questions.append(new_question)
        return new_question

    async def list_questions(
        self, theme_id: int | None = None
    ) -> list[Question]:
        if theme_id is None:
            return self.app.database.questions

        return list(question for question in self.app.database.questions if question.theme_id == theme_id)
