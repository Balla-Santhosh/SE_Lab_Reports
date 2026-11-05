"""
Lab 7 - Fuzz testing with Hypothesis
Name : Balla Santhosh
SRN  : PES1UG24AM063
Module under test: processor.py (water utility billing input processing)
"""
from hypothesis import given, settings, strategies as st
from processor import sanitize_meter_id, parse_consumption_readings, format_billing_summary


@settings(max_examples=500)
@given(st.text() | st.none())
def test_sanitize_meter_id_no_crash(s):
    try:
        result = sanitize_meter_id(s)
    except Exception as e:
        assert False, f"sanitize_meter_id crashed on {s!r} with: {type(e).__name__}: {e}"
    # properties: always a string, no forbidden symbols, no surrounding whitespace
    assert isinstance(result, str)
    for ch in "!@#$%":
        assert ch not in result
    assert result == result.strip()


@settings(max_examples=500)
@given(st.text() | st.none())
def test_parse_consumption_readings_safe(s):
    try:
        result = parse_consumption_readings(s)
    except Exception as e:
        assert False, f"parse_consumption_readings crashed on {s!r} with: {type(e).__name__}: {e}"
    # properties: always a list of ints
    assert isinstance(result, list)
    assert all(isinstance(r, int) for r in result)


@settings(max_examples=500)
@given(st.text() | st.none())
def test_format_billing_summary_safe(s):
    try:
        result = format_billing_summary(s)
    except Exception as e:
        assert False, f"format_billing_summary crashed on {s!r} with: {type(e).__name__}: {e}"
    # property: always returns a string
    assert isinstance(result, str)


# Targeted strategy: CSV of integers mixed with junk tokens
@given(st.lists(st.integers(min_value=-10**6, max_value=10**6)
                | st.sampled_from(["", " ", "abc", "1.5", "--3"]), min_size=1))
def test_parse_consumption_readings_structured(tokens):
    csv = ",".join(str(t) for t in tokens)
    try:
        result = parse_consumption_readings(csv)
    except Exception as e:
        assert False, f"parse_consumption_readings crashed on {csv!r} with: {type(e).__name__}: {e}"
    # every genuine integer token must survive parsing, in order
    expected = [t for t in tokens if isinstance(t, int)]
    assert result == expected


# Targeted strategy: Name:Usage:Zone records with sometimes-bad fields
@given(st.text(alphabet=st.characters(blacklist_characters=":"), max_size=10),
       st.integers(min_value=0, max_value=10**6).map(str) | st.sampled_from(["", "x", "-", "1e3"]),
       st.text(alphabet=st.characters(blacklist_characters=":"), max_size=10))
def test_format_billing_summary_structured(name, units, zone):
    record = f"{name}:{units}:{zone}"
    try:
        result = format_billing_summary(record)
    except Exception as e:
        assert False, f"format_billing_summary crashed on {record!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)
    if units.isdigit():
        assert f"billed {int(units) * 2} USD" in result
