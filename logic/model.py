import re
import warnings

import numpy as np

from pyclustering.cluster.kmeans import kmeans as pycl_kmeans
from pyclustering.cluster.elbow import elbow as pycl_elbow
from pyclustering.utils.metric import type_metric, distance_metric
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer

from sklearn.feature_extraction.text import TfidfVectorizer

from gensim.models import KeyedVectors
import pymystem3

from logic.preprocessor import TextPreprocessor
from misc.util import threadpool
from misc.config import Paths


np.warnings = warnings


mystem_tags_to_upos = {
    "A": "ADJ",
    "ADV": "ADV",
    "ADVPRO": "ADV",
    "ANUM": "ADJ",
    "APRO": "DET",
    "COM": "ADJ",
    "CONJ": "SCONJ",
    "INTJ": "INTJ",
    "NONLEX": "X",
    "NUM": "NUM",
    "PART": "PART",
    "PR": "ADP",
    "S": "NOUN",
    "SPRO": "PRON",
    "UNKN": "X",
    "V": "VERB",
}

word2vec_model = KeyedVectors.load_word2vec_format(
    Paths.word2vec_model,
    binary=False,
)
mystem = pymystem3.mystem.Mystem()

zero_array = np.zeros(300)


def get_word2vec_embeddings(document):
    tokens = mystem.analyze(document)
    document_vec = list()

    for token in tokens:
        if token["text"].strip() == "":
            continue
        if not token.get("analysis"):
            continue

        lemma = token["analysis"][0]["lex"]
        part_speech = token["analysis"][0]["gr"].split(",")[0].replace("=", "")
        part_speech = re.match(r"^[A-Z]*", part_speech).group(0)
        upos = mystem_tags_to_upos[part_speech]
        word = f"{lemma}_{upos}"

        try:
            word_vec = word2vec_model[word]
        except KeyError:
            document_vec.append(zero_array)
            continue

        document_vec.append(word_vec)

    return np.mean(document_vec, axis=0)


class SpreaderHat:
    def __init__(self, n_clusters="auto"):
        self.n_clusters = n_clusters
        self.kmeans_instance = None

    def train(self, train_data):
        if type(self.n_clusters) != int:
            if len(train_data) // 3 > 5:
                elbow_instance = pycl_elbow(
                    train_data,
                    2, 10
                )
                elbow_instance.process()
                self.n_clusters = elbow_instance.get_amount()
            else:
                self.n_clusters = min(len(train_data), max(0, len(train_data) // 3))

        metric = distance_metric(type_metric.EUCLIDEAN)
        start_centers = kmeans_plusplus_initializer(
            train_data, self.n_clusters
        ).initialize()
        self.kmeans_instance = pycl_kmeans(train_data, start_centers, metric=metric)
        self.kmeans_instance.process()

    def get_clusters(self):
        return self.kmeans_instance.get_clusters()

    def get_most_importance_cluster_words(self, prepared_texts, top=5):
        sum_answers = list()
        pycl_clusters = self.kmeans_instance.get_clusters()
        for i, cluster in enumerate(pycl_clusters):
            cluster_answers = list()
            for ans in cluster:
                cluster_answers.append(prepared_texts[ans])
            sum_answers.append(" ".join(cluster_answers))

        vectorizer = TfidfVectorizer()
        vectorizer.fit(sum_answers)
        tfidf_vectors = vectorizer.transform(sum_answers).toarray()
        feature_names = vectorizer.get_feature_names_out()

        result = {}
        for i, cluster in enumerate(pycl_clusters):
            features = list(zip(feature_names, tfidf_vectors[i]))
            features.sort(key=lambda s: s[1], reverse=True)
            top_features = features[:top]
            result[i] = {k: v for k, v in top_features}

        return result


@threadpool
def prediction_task(entries: list[str]) -> tuple[dict[int, dict[str, float]], tuple[tuple[int]]]:
    text_preprocessor = TextPreprocessor(entries)
    prepared_lines = text_preprocessor.clean_texts()

    embeddings = [get_word2vec_embeddings(ans) for ans in prepared_lines]

    spreader_hat = SpreaderHat(n_clusters="auto")
    spreader_hat.train(embeddings)

    clusters = spreader_hat.get_most_importance_cluster_words(prepared_lines, top=10)

    return clusters, spreader_hat.get_clusters()


async def predict(lines: list[str]) -> tuple[dict[int, dict[str, float]], tuple[tuple[int]]]:
    return await prediction_task(lines)
