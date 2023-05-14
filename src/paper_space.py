import os.path
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

from src.ontology_classes import Affiliation, Author

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))


def _get_forename(name):
    return name.split(" ")[0] if len(name.split(" ")) > 1 else ""


class PaperSet:

    def __init__(self, papers):
        self.papers = self.index_papers(papers)
        # self.encoder = SentenceTransformer("jamescalam/minilm-arxiv-encoder")
        self.encoder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.ner = pipeline("ner",
                            model=AutoModelForTokenClassification.from_pretrained(
                                "Babelscape/wikineural-multilingual-ner"),
                            tokenizer=AutoTokenizer.from_pretrained("Babelscape/wikineural-multilingual-ner")
                            )
        self.lda_model = None
        self.vectorizer = None
        self.topics = []
        if os.path.exists("../res/models/lda_model.pkl"):
            with open("../res/models/lda_model.pkl", "rb") as f:
                self.lda_model = pickle.load(f)
        if os.path.exists("../res/models/vectorizer.pkl"):
            with open("../res/models/vectorizer.pkl", "rb") as f:
                self.vectorizer = pickle.load(f)

        print("\rClustering", end='')
        self.clusterize()
        print("\rTopic Modeling", end='')
        self.topic_modeling()
        print("\rRecognizing entities", end='')
        self.find_entities()
        print("\rLinking authors", end='')
        self.all_authors = self.link_and_get_all_authors()
        print("\rLinking affiliations", end='')
        self.all_affiliations = self.link_and_get_affiliations()
        print("\rLinking journals", end='')
        self.all_journals = self.link_and_get_all_journals()

        self.enrich()

    def get_xml_papers(self):
        return {paper.title: paper for paper in self.papers.values() if paper.physical}

    def get_citation_papers(self):
        return {paper.title: paper for paper in self.papers.values() if not paper.physical}

    def encode_papers(self):
        encodable = self.get_xml_papers()
        return pd.DataFrame(self.encoder.encode([paper.abstract for paper in encodable.values()]),
                            index=[paper.title for paper in encodable.values()])

    def index_papers(self, papers):
        '''
        Creates Dictionary of papers where key is the papers title and value is the paper object, only for
        physical papers. Then, for papers created by citations, it creates another dictionary and then checks if the title
        of the paper is in the dictionary of physical papers. If it is, it changes the paper object to the physical paper

        :return:
        '''
        papers_dict = {paper.title: paper for paper in papers}
        ref_papers = {}
        for paper in papers:
            if paper.references:
                for i in range(len(paper.references)):
                    if paper.references[i].cites.title in papers_dict.keys():
                        paper.references[i].cites = papers_dict[paper.references[i].cites.title]
                        papers_dict[paper.references[i].cites.title].cited_by.append(paper.references[i])
                    else:
                        ref_papers[paper.references[i].cites.title] = paper.references[i].cites
                        papers_dict[paper.references[i].cites.title] = paper.references[i].cites
        self.citation_papers = ref_papers
        return papers_dict

    def encode_paper(self, paper):
        return pd.DataFrame(self.encoder.encode(paper.abstract), index=paper.filename)

    def preprocess_text(self, text):
        # Tokenize the text into individual words
        tokens = word_tokenize(text)
        # Remove stop words from the token list
        filtered_tokens = [word for word in tokens if not word.lower() in stop_words]
        # Join the remaining tokens back into a single string
        return ' '.join(filtered_tokens)

    def clusterize(self):
        encoded = self.encode_papers()
        clustering = AgglomerativeClustering(n_clusters=2, affinity='cosine', linkage='complete')
        assined_papers = pd.Series(clustering.fit_predict(encoded), index=encoded.index)
        for item, cluster in assined_papers.items():
            self.papers[item].cluster = cluster

    def _perform_lda(self, tokens, index):
        num_topics = 10
        if not self.lda_model:
            self.lda_model = LatentDirichletAllocation(n_components=num_topics, max_iter=500, learning_method='online')
            self.lda_model.fit(tokens)
            with open("../res/models/lda_model.pkl", "wb") as f:
                pickle.dump(self.lda_model, f)

        feature_names = self.vectorizer.get_feature_names_out()
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_words_idx = topic.argsort()[:-3:-1]
            self.topics.append(", ".join([feature_names[i] for i in top_words_idx]))

        for paper, token in zip(index, tokens):
            self.papers[paper].topic = self.topics[self.lda_model.transform(token).argmax()]

    def topic_modeling(self):
        df = pd.DataFrame([{'Title': paper.title, "abstract": self.preprocess_text(paper.abstract),
                            'label': paper.cluster} for paper in
                           self.get_xml_papers().values()])
        if not self.vectorizer:
            self.vectorizer = CountVectorizer()
            self.vectorizer.fit(df['abstract'])
            with open("../res/models/vectorizer.pkl", "wb") as f:
                pickle.dump(self.vectorizer, f)
        self._perform_lda(self.vectorizer.transform(df['abstract']), df['Title'])

    def find_entities(self):
        for paper in self.get_xml_papers().values():
            text = paper.acknowledgements.text
            ner_results = self.ner(text)
            processed_entities = self.process_entities(ner_results, text)
            paper.acknowledgements.acknowledges_org = list(
                map(lambda x: Affiliation(name=x["text"], ackowledged_by=[paper.acknowledgements]),
                    filter(lambda x: x["entity"] == "ORG", processed_entities)))
            paper.acknowledgements.acknowledges_people = list(
                map(lambda x: Author(forename=_get_forename(x["text"]), surname=x["text"].split(" ")[-1],
                                     acknowledged_by=[paper.acknowledgements]),
                    filter(lambda x: x["entity"] == "PER", processed_entities)))

    def link_and_get_all_authors(self):
        authors = []
        for paper in self.papers.values():
            for author in paper.authors:
                if author not in authors:
                    authors.append(author)
                else:
                    index = authors.index(author)
                    paper.authors.remove(author)
                    paper.authors.append(authors[index])
                    if authors[index] in paper.authors:
                        authors[index].writes.append(paper)
                        authors[index].ackowledged_by.extend(author.ackowledged_by)

        return authors

    def link_and_get_affiliations(self):
        affiliations = {}
        for paper in self.papers.values():
            for author in paper.authors:
                if author.affiliation not in affiliations:
                    affiliations[author.affiliation] = author.affiliation
                else:
                    previous_ack_by = author.affiliation.acknowledged_by
                    author.affiliation = affiliations[author.affiliation]
                    author.affiliation.acknowledged_by.extend(previous_ack_by)
        return affiliations

    def link_and_get_all_journals(self):
        journals = []
        for paper in self.papers.values():
            if paper.journal:
                if paper.journal not in journals:
                    journals.append(paper.journal)
                else:
                    index = journals.index(paper.journal)
                    paper.journal = journals[index]
                    journals[index].publishes.append(paper)

        return journals

    def process_entities(self, entities, text):
        org_start = None
        org_end = None
        people_start = None
        people_end = None
        new_entities = []

        for i, entity in enumerate(entities):
            if entity['entity'] == 'B-ORG':
                org_start = entity['start']
                org_end = entity['end']
            elif entity['entity'] == 'I-ORG':
                org_end = entity['end']
            elif entity['entity'] == 'B-PER':
                people_start = entity['start']
                people_end = entity['end']
            elif entity['entity'] == 'I-PER':
                people_end = entity['end']

            if org_start is not None and org_end is not None:
                if i == len(entities) - 1 or entities[i + 1]['entity'] != 'I-ORG':
                    new_entities.append({'entity': 'ORG', "text": text[org_start:org_end]})
                    org_start = None
            if people_start is not None and people_end is not None:
                if i == len(entities) - 1 or entities[i + 1]['entity'] != 'I-PER':
                    new_entities.append({'entity': 'PER', "text": text[people_start:people_end]})
                    people_start = None

        return new_entities

    def enrich_journals(self):
        for journal in self.all_journals:
            journal.enrich()

    def enrich_affiliations(self):
        for affiliation in self.all_affiliations:
            affiliation.enrich()

    def enrich_authors(self):
        print(len(self.all_authors))
        for author in self.all_authors:
            print("\rEnriching authors: {}, {}/{}                                              ".format(f'{author.forename} {author.surname}', self.all_authors.index(author), len(self.all_authors)), end='')
            author.enrich()

    def enrich(self):
        print("\rEnriching affiliations", end='')
        self.enrich_affiliations()
        print("\rEnriching authors                                                                ", end='')
        self.enrich_authors()
        print("\rEnriching journals                                                                ", end='')
        self.enrich_journals()
