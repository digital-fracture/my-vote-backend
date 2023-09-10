from pathlib import Path

from wordcloud import WordCloud

from PIL import Image, ImageDraw, ImageFont
import numpy as np

from misc.util import get_temp_file_path, threadpool
from misc.config import Paths


cloud = WordCloud(
    width=800,
    height=600,
    background_color="#525252",
    colormap="Set3",
    font_path=str(Paths.wordcloud_font),
    mask=np.array(Image.open(Paths.wordcloud_mask)),
    contour_width=10,
    contour_color="#ccff00"
)

image_font = ImageFont.truetype(str(Paths.wordcloud_font), 120)


@threadpool
def generation_task(frequencies: dict[str, float], path: Path) -> None:
    cloud.generate_from_frequencies(frequencies).to_file(path)


async def generate(frequencies: dict[str, float]) -> Path:
    await generation_task(frequencies, path := get_temp_file_path("png"))

    return path


@threadpool
def concatenation_task(sources: list[Path], destination: Path) -> None:
    result = Image.new("RGB", (800 * 4, 600 * 4), "#525252")

    for y in range(4):
        for x in range(4):
            index = y * 4 + x
            if index == len(sources):
                break

            img = Image.open(sources[index])
            draw = ImageDraw.ImageDraw(img)

            draw.text((200, 20), f"#{index + 1}", font=image_font, fill="#ffffff")

            result.paste(img, (x * 800, y * 600))

        else:
            continue

        break

    result.save(destination)


async def concatenate(sources: list[Path]) -> Path:
    await concatenation_task(sources, path := get_temp_file_path("png"))

    return path
