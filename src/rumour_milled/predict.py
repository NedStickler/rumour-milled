import joblib


trained_models_paths = {
    "tfidf_logistic_regression": "models/tfidf_logisticregression.pkl"
}


def predict(model: str, values):
    model = joblib.load(trained_models_paths.get(model))
    return model.predict(values)
