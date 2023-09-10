from string import punctuation
import re

import pymystem3

from misc.config import Paths


class BadWordChecker:
    with open(Paths.bad_words, "r") as file:
        words = set([i.replace("\n", "") for i in file.readlines()])

    def __init__(self):
        pass

    def is_bad_word(self, word):
        return word in self.words

    def is_bad_text(self, text):
        return len(set(text) & self.words) > 0


class EmojiConverter:
    d = dict()
    with open(Paths.emojis, "r") as file:
        data = file.readlines()[0].split("@")
        for i in data:
            a, b = i.split(";")
            d[a] = b

    def __init__(self):
        pass

    def convert_string(self, s):
        for i in self.d.keys():
            s = s.replace(i, f" {self.d[i]} ")
        return s


with open(Paths.stopwords, "r") as file:
    russian_stopwords = tuple(map(lambda line: line.strip(), file.read().strip().split("\n")))

mystem = pymystem3.mystem.Mystem()
emoji_converter = EmojiConverter()
bad_word_checker = BadWordChecker()


class TextPreprocessor:
    def __init__(self, texts):
        self.raw_documents = texts
        self.prepared_texts = ""

    @staticmethod
    def lemmatize_text(document):
        tokens = mystem.lemmatize(document)
        new_tokens = list()
        for token in tokens:
            if token not in russian_stopwords and token != " ":
                if token.strip() not in punctuation:
                    # if len(token) > 2:
                    new_tokens.append(token)
        document = " ".join(new_tokens)

        return document

    @staticmethod
    def is_bad_text(text):
        return bad_word_checker.is_bad_text(text)

    def clean_texts(
        self,
        texts=None,
        lemmatization=True,
        emoji_decode=True,
        only_censored_texts=True,
    ):
        """
        Remove all the special characters
        Remove all single characters
        Remove single characters from the start
        Substituting multiple spaces with single space
        Replace "ё" with "е"
        Converting to lowercase
        and other optional functions
        """

        only_censored_texts = lemmatization & only_censored_texts

        if texts is None:
            texts = self.raw_documents
        documents = []

        for sen in range(0, len(texts)):
            document = str(texts[sen])

            if emoji_decode:
                document = emoji_converter.convert_string(document)
            # Remove all the special characters
            document = re.sub(r"\W", " ", document)
            # remove all single characters
            document = re.sub(r"\s+[a-zA-Zа-яА-Я0-9]\s+", " ", document)
            # Remove single characters from the start
            document = re.sub(r"\^[a-zA-Zа-яА-Я0-9]\s+", " ", document)
            # Substituting multiple spaces with single space
            document = re.sub(r"\s+", " ", document, flags=re.I)
            document = re.sub("ё", "е", document.lower())
            # Removing prefixed 'b'
            document = re.sub(r"^b\s+", "", document)
            # Converting to lowercase
            document = document.lower()

            # Lemmatization
            if lemmatization:
                document = self.lemmatize_text(document)

                if only_censored_texts:
                    if self.is_bad_text(document):
                        continue
            documents.append(document)
        self.prepared_texts = documents
        return documents
