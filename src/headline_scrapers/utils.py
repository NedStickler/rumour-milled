def clean(headlines: list[str]) -> list[str]:
    cleaned_headlines = [
        headline.replace("\n", " ").replace("  ", " ").strip() for headline in headlines
    ]
    cleaned_headlines = [
        headline for headline in cleaned_headlines if len(headline.split(" ")) > 3
    ]
    cleaned_headlines = [
        headline for headline in cleaned_headlines if headline not in ["", " "]
    ]
    return list(set(cleaned_headlines))
