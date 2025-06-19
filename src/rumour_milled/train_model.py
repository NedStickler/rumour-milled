from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from rumour_milled.preprocessing import preprocess
import numpy as np


def train_model(X, y, model, embedding) -> Pipeline:
    """Train a model using the TFIDF vectoriser.

    Args:
        X (_type_): Training data.
        y (_type_): Labels.
        model (_type_): Model to train.
        params (_type_): Model parameters.

    Returns:
        Pipeline: Trained training pipeline.
    """
    model_name = model.__name__.lower()
    embedding_name = embedding.__name__.lower()
    pipeline = Pipeline(
        [
            ("clean", FunctionTransformer(np.vectorize(preprocess))),
            (embedding_name, embedding()),
            (model_name, model()),
        ]
    )
    pipeline.fit(X, y)
    return pipeline
