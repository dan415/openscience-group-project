import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer, util


class PaperModeling:

    def __init__(self):
        self.encoder = SentenceTransformer("jamescalam/minilm-arxiv-encoder")
        self.NER = None
        with open("../res/models/clustering_model.pkl", "rb") as f:
            self.clustering_model = pickle.load(f)
        with open("../res/models/clustering_topics.pkl", "rb") as f:
            self.clustering_topics = pickle.load(f)

    def encode_paper(self, paper):
        return pd.DataFrame(self.encoder.encode(paper.abstract), index=paper.filename)

    def assign_to_cluster(self, paper):
        most_probable_cluster = self.clustering_topics[self.clustering_model.predict(self.encode_paper(paper))]
        return most_probable_cluster, self.clustering_topics[most_probable_cluster]

    def get_entities(self, paper):
        return self.NER(paper.abstract)
