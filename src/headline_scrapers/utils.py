def clean(headlines: list[str]) -> list[str]:
    """Clean and filter a list of headlines.

    Removes newlines, extra spaces, headlines with fewer than four words, and empty strings. Returns unique cleaned headlines.

    Args:
        headlines (list[str]): List of raw headline strings.

    Returns:
        list[str]: List of cleaned, unique headlines.
    """
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
