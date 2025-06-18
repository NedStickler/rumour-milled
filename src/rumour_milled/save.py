import joblib


def save_model(model, path) -> None:
    joblib.dump(model, path)
