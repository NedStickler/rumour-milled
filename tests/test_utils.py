from rumour_milled.utils import clean_headlines


def test_removes_newlines_trims_and_keeps_long_enough():
    raw = ["  Hello\nWorld  from  AI  "]
    out = clean_headlines(raw)
    assert set(out) == {"Hello World from AI"}


def test_filters_short_and_empty():
    raw = [
        "", " ", "\n\n",
        "one two three",
        "one two three four",
    ]
    out = clean_headlines(raw)
    assert "one two three four" in out
    assert "one two three" not in out
    assert "" not in out and " " not in out


def test_deduplicates():
    raw = [
        "A long enough headline here",
        "A long enough headline here",
        "A long  enough  headline  here",
    ]
    out = clean_headlines(raw)
    assert set(out) == {"A long enough headline here"}


def test_multiple_spaces_reduce_but_may_leave_double():
    raw = ["word    word two three"]
    out = clean_headlines(raw)
    assert len(out) == 1
    cleaned = out[0]
    assert "\n" not in cleaned
    assert cleaned == "word  word two three"