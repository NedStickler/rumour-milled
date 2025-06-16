from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from src.rumour_milled.preprocessing import preprocess
import joblib


def train_model(X, y, model, params={}) -> Pipeline:
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
    pipeline = Pipeline(
        [
            ("clean", FunctionTransformer(lambda x: x.apply(preprocess))),
            ("tfidf", TfidfVectorizer()),
            (model_name, model(**params)),
        ]
    )
    pipeline.fit(X, y)
    return pipeline
