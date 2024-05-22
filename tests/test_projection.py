from io import StringIO

from lxml import etree

from udl2xml.main import convert
from udl2xml.util import get_line
from udl2xml.projection import handle_projection


def test_basic():
    """Test projection with keywords"""
    
    udl = "Projection A As Test.P;"
    prj = call_handler(udl)
    
    assert prj.attrib.get('name') == 'A', "Projection name present"
    assert (el := prj.find('Type')) is not None, "Type element present"
    assert el.text == 'Test.P', "Type has correct value"


def test_parameter():
    """Test projection with parameter"""
    
    udl = "Projection A As Test.P(DisableMulticompile = 1);"
    prj = call_handler(udl)
    
    assert (lst := prj.xpath("./Parameter[@name='DisableMulticompile']")), 'Parameter DisableMulticompile present'
    assert lst[0].attrib.get('value') == '1', "Parameter DisableMulticompile has correct value"


def test_keyword():
    """Test projection with keyword"""
    
    udl = "Projection A As Test.P [ Internal ];"
    prj = call_handler(udl)
    
    assert (el := prj.find('Internal')) is not None, "Internal element present"
    assert el.text == '1', "Internal has correct value"


def test_parameter_and_keyword():
    """Test projection with both parameter and keyword"""
    
    udl = "Projection A As Test.P(DisableMulticompile = 1) [ Internal ];"
    prj = call_handler(udl)
    
    assert (lst := prj.xpath("./Parameter[@name='DisableMulticompile']")), 'Parameter DisableMulticompile present'
    assert lst[0].attrib.get('value') == '1', "Parameter DisableMulticompile has correct value"
    
    assert (el := prj.find('Internal')) is not None, "Internal element present"
    assert el.text == '1', "Internal has correct value"



def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
Projection A As Test.P;
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
    
    handle_projection(root, stream, line, None)
    
    assert len(root) == 1, 'Element added'
    return root[0]

