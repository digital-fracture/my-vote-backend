from os import environ
from typing import Any

import orjson
import aiofiles
from charset_normalizer import from_bytes

from fastapi import FastAPI, Request, UploadFile, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from supabase import create_client

from logic import model, extend, wordcloud_generation
from misc.data_models import Quiz, Form
from misc.util import get_temp_file_path
from misc.config import Paths


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory=Paths.static_dir), name="static")


templates = Jinja2Templates(Paths.templates_dir)


database = create_client(
    environ.get("SUPABASE_URL"),
    environ.get("SUPABASE_KEY")
)


@app.get("/")
async def index():
    return {"response": "I <3 Scarlett"}


@app.post("/api/main")
async def api_main(file: UploadFile):
    contents = str(from_bytes(await file.read()).best()).strip()
    data = orjson.loads(contents)

    answers = list(map(lambda entry: entry["answer"], data["answers"]))

    clusters, indices = await model.predict(answers)
    for group_index, group in enumerate(indices):
        for index in group:
            data["answers"][index]["cluster"] = tuple(clusters[group_index].keys())[0]

    async with aiofiles.open(path := get_temp_file_path("json"), "wb") as file:
        await file.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    return FileResponse(
        path,
        media_type="text/plain",
        filename="extended.json"
    )


@app.post("/api/extend/txt")
async def api_extend_txt(file: UploadFile):
    contents = str(from_bytes(await file.read()).best()).strip()
    extended = await extend.predict(contents.split("\n"))

    async with aiofiles.open(path := get_temp_file_path("txt"), "w") as file:
        await file.write("\n".join(extended))

    return FileResponse(
        path,
        media_type="text/plain",
        filename="extended.txt"
    )


@app.post("/api/extend/json")
async def api_extend_json(file: UploadFile):
    contents = str(from_bytes(await file.read()).best()).strip()
    data = orjson.loads(contents)

    extended = await extend.predict(tuple(map(lambda answer: answer["answer"], data["answers"])))
    for index, answer in enumerate(data["answers"]):
        answer["answer"] = extended[index]

    async with aiofiles.open(path := get_temp_file_path("json"), "wb") as file:
        await file.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    return FileResponse(
        path,
        media_type="text/plain",
        filename="extended.json"
    )


@app.post("/quiz/create")
async def create_quiz(quiz: Quiz):
    quiz_id = database.table("quiz").insert(
        {
            "creator_id": (
                database
                .table("User")
                .select("id")
                .eq("email", quiz.email)
                .execute()
                .data[0]["id"]
            ),
            "title": quiz.title
        }
    ).execute().data[0]["id"]

    database.table("quiz_question").insert(
        [
            {
                "quiz_id": quiz_id,
                "question": question.question,
                "answers": tuple(map(lambda answer: answer.answer, question.answers)),
                "correct_answer": next(filter(lambda answer: answer.is_correct, question.answers)).answer
            }
            for question in quiz.questions
        ]
    ).execute()


@app.get("/quiz/{quiz_id}")
async def get_quiz(request: Request, quiz_id: int):
    return templates.TemplateResponse(
        "quiz.html",
        {
            "request": request,
            "id": quiz_id,
            "title": (
                database
                .table("quiz")
                .select("title")
                .eq("id", quiz_id)
                .execute()
                .data[0]["title"]
            ),
            "questions": (
                database
                .table("quiz_question")
                .select("id", "question", "answers")
                .eq("quiz_id", quiz_id)
                .execute()
                .data
            )
        }
    )


@app.post("/quiz/{quiz_id}/submit_answer")
async def submit_quiz_answer(quiz_id: int, answers: dict[int, str]):
    submission_ids = tuple(map(
        lambda entry: entry["submission_id"],
        database.table("quiz_user_answer").select("submission_id").execute().data
    ))
    new_submission_id = (max(submission_ids) if submission_ids else 0) + 1

    correct_answers = tuple(map(
        lambda entry: entry["correct_answer"],
        database
        .table("quiz_question")
        .select("correct_answer")
        .in_("id", answers.keys())
        .execute()
        .data
    ))

    database.table("quiz_user_answer").insert(
        [
            {
                "submission_id": new_submission_id,
                "quiz_id": quiz_id,
                "question_id": question_id,
                "answer": answer,
                "is_correct": answer == correct_answers[index]
            }
            for index, (question_id, answer) in enumerate(answers.items())
        ]
    ).execute()

    return {"submission_id": new_submission_id}


# noinspection PyUnusedLocal
@app.get("/quiz/{quiz_id}/submissions/{submission_id}")
async def get_quiz_submission(quiz_id: int, submission_id: int):
    return (
        database
        .table("quiz_user_answer")
        .select("answer", "is_correct")
        .eq("submission_id", submission_id)
        .execute()
        .data
    )


@app.post("/form/create")
async def create_form(form: Form):
    form_id = database.table("form").insert(
        {
            "creator_id": (
                database
                .table("User")
                .select("id")
                .eq("email", form.email)
                .execute()
                .data[0]["id"]
            ),
            "title": form.title
        }
    ).execute().data[0]["id"]

    database.table("form_question").insert(
        [
            {
                "form_id": form_id,
                "question": question.question
            }
            for question in form.questions
        ]
    ).execute()


@app.get("/form/{form_id}")
async def get_form(request: Request, form_id: int):
    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "id": form_id,
            "title": (
                database
                .table("form")
                .select("title")
                .eq("id", form_id)
                .execute()
                .data[0]["title"]
            ),
            "questions": (
                database
                .table("form_question")
                .select("id", "question")
                .eq("form_id", form_id)
                .execute()
                .data
            )
        }
    )


@app.post("/form/{form_id}/submit_answer")
async def submit_form_answer(form_id: int, answers: dict[int, str]):
    submission_ids = tuple(map(
        lambda entry: entry["submission_id"],
        database.table("form_user_answer").select("submission_id").execute().data
    ))
    new_submission_id = (max(submission_ids) if submission_ids else 0) + 1

    database.table("form_user_answer").insert(
        [
            {
                "submission_id": new_submission_id,
                "form_id": form_id,
                "question_id": question_id,
                "answer": answer,
            }
            for question_id, answer in answers.items()
        ]
    ).execute()


@app.post("/form/all")
async def get_all_forms(email: str = Body(embed=True), domain: str = Body(embed=True)):
    user_id = (
        database
        .table("User")
        .select("id")
        .eq("email", email)
        .execute()
        .data[0]["id"]
    )

    return list(
        map(
            lambda entry: {**entry, "link": f"{domain}form/{entry['id']}"},
            database
            .table("form")
            .select("id", "title")
            .eq("creator_id", user_id)
            .execute()
            .data
        )
    )


@app.post("/form/result")
async def form_result(form_id: int = Body(embed=True)):
    question_ids = tuple(map(
        lambda entry: entry["id"],
        database.table("form_question").select("id").eq("form_id", form_id).execute().data
    ))

    all_needed_answers = (
        database
        .table("form_user_answer")
        .select("question_id", "answer")
        .in_("question_id", question_ids)
        .execute()
        .data
    )

    if not all_needed_answers:
        return

    answers_2d_list: list[list[str]] = [
        list(map(
            lambda entry: entry["answer"],
            filter(
                lambda entry: entry["question_id"] == question_id,
                all_needed_answers
            )
        ))
        for question_id in question_ids
    ]

    wordcloud_paths = []
    for answers in answers_2d_list:
        clusters, _ = await model.predict(answers)
        frequencies = {
            key: value
            for cluster in clusters.values()
            for key, value in cluster.items()
            if value > 0.1
        }
        wordcloud_paths.append(await wordcloud_generation.generate(frequencies))

    return FileResponse(
        await wordcloud_generation.concatenate(wordcloud_paths),
        media_type="image/png",
        filename="wordcloud.png"
    )


@app.post("/wordcloud")
async def get_wordcloud(frequencies: dict[str, float]):
    return FileResponse(
        await wordcloud_generation.generate(frequencies),
        media_type="image/png",
        filename="wordcloud.png"
    )
