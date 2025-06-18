from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from rumour_milled.train_model import train_model
from rumour_milled.load import load_data
from rumour_milled.save import save_model
from rumour_milled.encoders import SentenceTransformerEncoder


if __name__ == "__main__":
    data = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        data["title"], data["fake_news"], test_size=0.2, random_state=42
    )

    # logistic_regression = train_model(
    #     X_train, y_train, LogisticRegression, TfidfVectorizer
    # )
    # random_forest = train_model(
    #     X_train, y_train, RandomForestClassifier, TfidfVectorizer
    # )
    # gradient_boosting = train_model(
    #     X_train, y_train, GradientBoostingClassifier, TfidfVectorizer
    # )
    # xgboost = train_model(X_train, y_train, XGBClassifier, TfidfVectorizer)

    logistic_regression_transformer = train_model(
        X_train, y_train, LogisticRegression, SentenceTransformerEncoder
    )

    # save_model(logistic_regression, "models/logisticregression_tfidf.pkl")
    # save_model(random_forest, "models/randomforestclassifier_tfidf.pkl")
    # save_model(gradient_boosting, "models/gradientboostingclassifier_tfidf.pkl")
    # save_model(random_forest, "models/xgbclassifier_tfidf.pkl")
    save_model(
        logistic_regression_transformer, "models/logisticregression_allminilml6v2.pkl"
    )
