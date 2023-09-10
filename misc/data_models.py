from pydantic import BaseModel


class QuizAnswer(BaseModel):
    answer: str
    is_correct: bool


class QuizQuestion(BaseModel):
    question: str
    answers: list[QuizAnswer]


class Quiz(BaseModel):
    email: str
    title: str
    questions: list[QuizQuestion]


class FormQuestion(BaseModel):
    question: str


class Form(BaseModel):
    email: str
    title: str
    questions: list[FormQuestion]
