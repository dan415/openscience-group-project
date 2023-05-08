from datasets import load_dataset, Features
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sentence_transformers import SentenceTransformer, util

download = False

if download:
    dataset = load_dataset(
        "scientific_papers",
        "arxiv",
        data_dir="../../datasets",
        features=Features({"abstract": "string"})
    )


model = SentenceTransformer("jamescalam/minilm-arxiv-encoder")
