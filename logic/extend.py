from threading import Thread
import asyncio
from typing import Iterable

from transformers import pipeline

from misc.util import threadpool


fred_pipeline = pipeline("text2text-generation", model="SiberiaSoft/SiberianFRED-T5-XL")


@threadpool
def prediction_task(lines: Iterable[str]) -> list[str]:
    return [
        str(
            fred_pipeline(
                f"<SC6>Человек: Дополни предложение  {text}...  Ответ: <extra_id_0>",
                do_sample=True,
                temperature=0.1,
                max_length=10
            )[0]["generated_text"]
        ).replace("<extra_id_0>", "")
        for text in lines
    ]


async def predict(lines: Iterable[str]) -> list[str]:
    return await prediction_task(lines)
