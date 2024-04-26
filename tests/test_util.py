import pytest

from util import extract, get_quoted_string


def test_extract_isfull():
    """Test extracting when there is no other data"""
    
    data = '[a,b,c]'
    ex = extract(data)
    
    assert ex == data, "Extracted data is full string"


def test_extract_parens():
    """Tests extracting parenthesis"""
    
    data = "()abc()xxx"
    ex = extract(data)
    
    assert ex == '()', "Stop at close parenthesis"


def test_extract_nested_parens():
    """Tests extracting (nested) parenthesis"""
    
    data = "(())xxx"
    ex = extract(data)
    
    assert ex == '(())', "Ignore embedded parenthesis"


def test_extract_quoted_parens():
    """Tests extracting parenthesis"""
    
    data = '(")")xxx'
    ex = extract(data)
    
    assert ex == '(")")', "Ignore quoted closing parenthesis"


def test_extract_ignore_quote():
    """Tests ignoring doubled quote"""
    
    data = '("")"")xxx'
    ex = extract(data)
    
    assert ex == '("")', "Ignore doubled quote"


def test_extract_raises_on_unknown_delim():
    """Tests that an unknown delimiter raises"""
    
    data = '"[]'
    with pytest.raises(ValueError) as e:
        ex = extract(data)
    assert 'Unrecognised delimiter' in e.value.args[0], "Appropriate error message"


def test_extract_embedded():
    """Test bare close bracket inside curly braces is ignored"""
    
    data = """[ SqlComputeCode = { Set a=3,b=1,z=a]b } ];"""
    
    ex = extract(data)
    assert ex == data[:-1], "Bracket in SqlComputeCode recogized"


# -----

def test_quoted_string_normal():
    """Simple quoted string"""
    
    test = '"abc def" the rest'
    expect = '"abc def"'
    value = get_quoted_string(test)
    assert value == expect, f"Expected '{expect}', got '{value}"


def test_quoted_string_embedded_quote():
    """Embedded quote recognized"""
    
    test = '"a""b" the rest'
    expect = '"a""b"'
    value = get_quoted_string(test)
    assert value == expect, f"Expected '{expect}', got '{value}"


def test_quoted_string_unmatched():
    """Unmatched quotes raises ValueError"""
    
    test = '"abc""'
    
    with pytest.raises(ValueError) as e:
        value = get_quoted_string(test)
    assert 'Unmatched quotes' in e.value.args[0], "Correct error message"


def test_quoted_string_no_end():
    """No end quote raises ValueError"""

    test = '"abc'
    
    with pytest.raises(ValueError) as e:
        value = get_quoted_string(test)
    assert 'scanning for close quote' in e.value.args[0], "Correct error message"

