from pathlib import Path
from tempfile import gettempdir


class Paths:
    wordcloud_font = Path("resources/fonts/Inter.ttf")
    wordcloud_mask = Path("resources/images/wordcloud_mask.png")

    bad_words = Path("resources/datasets/bad_words.txt")
    emojis = Path("resources/datasets/emojis.txt")
    stopwords = Path("resources/datasets/stopwords.txt")

    word2vec_model = Path("resources/keyed_vectors.vec.gz")

    static_dir = Path("resources/static")
    templates_dir = Path("resources/templates")

    temp_dir = Path(gettempdir(), "kruase")


Paths.temp_dir.mkdir(exist_ok=True)
