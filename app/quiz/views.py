from aiohttp_apispec import request_schema

from app.quiz.models import Answer
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    async def post(self):
        await self.authorize()
        theme = await self.store.quizzes.create_theme(title=self.data["title"])
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    async def get(self):
        await self.authorize()
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    async def post(self):
        await self.authorize()
        answers = [Answer(**answer) for answer in self.data["answers"]]
        question = await self.store.quizzes.create_question(
            title=self.data["title"],
            theme_id=self.data["theme_id"],
            answers=answers,
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    async def get(self):
        await self.authorize()
        theme_id = self.request.query.get("theme_id")
        questions = await self.store.quizzes.list_questions(
            theme_id=int(theme_id) if theme_id is not None else None
        )
        return json_response(data=ListQuestionSchema().dump({"questions": questions}))
