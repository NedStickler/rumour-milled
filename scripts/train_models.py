from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from rumour_milled.train_model import train_model
from rumour_milled.load import load_data
from rumour_milled.save import save_model
from rumour_milled.encoders import SentenceTransformerVectoriser
from tqdm import tqdm


if __name__ == "__main__":
    data = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        data["title"], data["fake_news"], test_size=0.2, random_state=42
    )

    models = [
        LogisticRegression,
        RandomForestClassifier,
        GradientBoostingClassifier,
        XGBClassifier,
    ]
    encoders = [TfidfVectorizer, SentenceTransformerVectoriser]

    for model in tqdm(
        models, bar_format="{l_bar}{bar:10}{r_bar}", desc="Training models"
    ):
        model_name = model.__name__.lower()
        for encoder in encoders:
            encoder_name = encoder.__name__.lower()
            save_model(
                train_model(X_train, y_train, model, encoder),
                f"models/{model_name}_{encoder_name}.pkl",
            )
