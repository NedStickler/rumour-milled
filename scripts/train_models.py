from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from rumour_milled.train_model import train_model
from rumour_milled.load import load_data
from rumour_milled.save import save_model


if __name__ == "__main__":
    data = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        data["title"], data["fake_news"], test_size=0.2, random_state=42
    )
    logistic_regression = train_model(
        X_train, y_train, LogisticRegression, TfidfVectorizer
    )
    save_model(logistic_regression, TfidfVectorizer)
