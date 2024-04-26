from io import StringIO

from lxml import etree

from main import convert
from util import get_line
from index import handle_index


# Index TestIdx On (a, b, "quo_ted") [ Data = (b, a), SqlName = SqlIndex, Type = index ];

def test_on_single_prop():
    """Test index on single property"""
    
    udl = "Index Test On a;"
    idx = call_handler(udl)
    assert (el := idx.find('Properties')) is not None, 'Properties element present'
    assert el.text == 'a', "Property extracted"


def test_on_multiple_props():
    """Test index on multiple properties"""
    
    udl = "Index Test On (a, b);"
    idx = call_handler(udl)
    assert (el := idx.find('Properties')) is not None, 'Properties element present'
    assert el.text == 'a,b', "Properties extracted, space removed"


def test_quoted_prop():
    """Test index on property with quoted name"""
    
    udl = 'Index Test On ("quo_ted");'
    idx = call_handler(udl)
    assert (el := idx.find('Properties')) is not None, 'Properties element present'
    assert el.text == '"quo_ted"', "Property extracted with quotes"


def test_single_data():
    """Test index with single data property"""
    
    udl = "Index Test On a [ Data = a ];"
    idx = call_handler(udl)
    assert (el := idx.find('Data')) is not None, 'Data element present'
    assert el.text == 'a', "Property extracted"


def test_multiple_data():
    """Test index with multiple data properties"""
    
    udl = "Index Test On (a, b) [ Data = (a, b) ];"
    idx = call_handler(udl)
    assert (el := idx.find('Data')) is not None, 'Data element present'
    assert el.text == 'a,b', "Properties extracted, space removed"


def test_bool_kwds():
    """Test index with various boolean keywords"""
    
    # This combination isn't actually valid, but that doesn't matter for the test.
    udl = "Index Test On a [ Abstract, Deprecated, Internal, Unique, IdKey, PrimaryKey ];"
    idx = call_handler(udl)
    
    assert (el := idx.find('Abstract')) is not None, 'Abstract element present'
    assert el.text == '1', "Abstract element has value 1"
    
    assert (el := idx.find('Deprecated')) is not None, 'Deprecated element present'
    assert el.text == '1', "Deprecated element has value 1"
    
    assert (el := idx.find('Internal')) is not None, 'Internal element present'
    assert el.text == '1', "Internal element has value 1"
    
    assert (el := idx.find('Unique')) is not None, 'Unique element present'
    assert el.text == '1', "Unique element has value 1"
    
    assert (el := idx.find('IdKey')) is not None, 'IdKey element present'
    assert el.text == '1', "IdKey element has value 1"
    
    assert (el := idx.find('PrimaryKey')) is not None, 'PrimaryKey element present'
    assert el.text == '1', "PrimaryKey element has value 1"


def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
Index a On a;
}
""".lstrip()
    
    xml = convert(udl).encode()
    root = etree.fromstring(xml)
    
    assert (doc := root.find('**/Description')) is not None, 'Description element present'
    assert doc.text == '\nThis is the documentation'


def call_handler(udl:str) -> etree._Element:
    """Helper to call the handler method"""
    
    root = etree.Element("dummy")
    root.text = '\n'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_index(root, stream, line, None)
    
    assert len(root) == 1, 'Element added'
    return root[0]

