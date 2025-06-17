import joblib


def save_model(model, embedding) -> None:
    model_name = model.__name__.lower()
    embedding_name = embedding.__name__.lower()
    joblib.dump(model, f"models/{model_name}_{embedding_name}.pkl")
