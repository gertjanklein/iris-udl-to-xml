from io import StringIO

from lxml import etree

from main import convert
from property import handle_property
from util import get_line


def test_bare():
    """Property without a type"""
    
    root = etree.Element("dummy")
    udl = 'Property a;'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_property(root, stream, line, None)
    
    assert len(root), 'Property added'
    el = root[0]
    assert el.tag == 'Property', 'Property has correct tag'
    assert el.attrib.get('name') == 'a', 'Property has correct name'
    
    assert (sel := el.find('Type')) is None, 'No Type element present'
    


def test_array():
    """Array Of converted to collection=array"""
    
    root = etree.Element("dummy")
    udl = 'Property a As array Of %String;'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_property(root, stream, line, None)
    
    assert len(root), 'Property added'
    el = root[0]
    assert el.tag == 'Property', 'Property has correct tag'
    assert el.attrib.get('name') == 'a', 'Property has correct name'
    
    assert (sel := el.find('Type')) is not None, 'Type element present'
    assert sel.text == '%String', 'Type has correct value'
    
    assert (sel := el.find('Collection')) is not None, 'Collection element present'
    assert sel.text == 'array', 'Collection is array'


def test_list():
    """List Of converted to collection=list"""
    
    root = etree.Element("dummy")
    udl = 'Property a As list Of %String;'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_property(root, stream, line, None)
    
    assert len(root), 'Property added'
    el = root[0]
    assert el.tag == 'Property', 'Property has correct tag'
    assert el.attrib.get('name') == 'a', 'Property has correct name'
    
    assert (sel := el.find('Type')) is not None, 'Type element present'
    assert sel.text == '%String', 'Type has correct value'
    
    assert (sel := el.find('Collection')) is not None, 'Collection element present'
    assert sel.text == 'list', 'Collection is list'


def test_relationship():
    """Relationship becomes property"""
    
    root = etree.Element("dummy")
    udl = "Relationship f As Test.Test3 [ Cardinality = many, Inverse = Inverse ];"
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_property(root, stream, line, None)
    
    assert len(root), 'Property added'
    el = root[0]
    assert el.tag == 'Property', 'Property has correct tag'
    assert el.attrib.get('name') == 'f', 'Property has correct name'
    
    assert (sel := el.find('Type')) is not None, 'Type element present'
    assert sel.text == 'Test.Test3', 'Type has correct value'
    
    assert (sel := el.find('Relationship')) is not None, 'Relationship element present'
    assert sel.text == '1', 'Relationship has correct value'
    
    assert (sel := el.find('Cardinality')) is not None, 'Cardinality element present'
    assert sel.text == 'many', 'Cardinality has correct value'
    
    assert (sel := el.find('Inverse')) is not None, 'Inverse element present'
    assert sel.text == 'Inverse', 'Inverse has correct value'


def test_quoted_name():
    """Property with quoted name"""
    
    root = etree.Element("dummy")
    udl = 'Property "a_""_b";'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_property(root, stream, line, None)
    
    assert len(root), 'Property added'
    el = root[0]
    assert el.tag == 'Property', 'Property has correct tag'
    assert el.attrib.get('name') == 'a_"_b', 'Property has correct name'


def test_parameters():
    """Parameters parsed and present"""
    
    root = etree.Element("dummy")
    udl = 'Property a As %String(a="A string", b = 5);'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_property(root, stream, line, None)
    
    assert len(root), 'Property added'
    el = root[0]
    assert el.tag == 'Property', 'Property has correct tag'
    assert el.attrib.get('name') == 'a', 'Property has correct name'
    
    assert (sel := el.find('Parameter[@name="a"]')) is not None, 'Parameter present'
    assert sel.attrib['value'] == 'A string', 'Parameter has correct value'
    
    assert (sel := el.find('Parameter[@name="b"]')) is not None, 'Parameter present'
    assert sel.attrib['value'] == '5', 'Parameter has correct value'


def test_initial_expression():
    """Quotes around initialexpression stay as-is"""
    
    root = etree.Element("dummy")
    udl = 'Property a As %String[ ClientName = "a b", InitialExpression = "abc" ];'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_property(root, stream, line, None)
    
    assert len(root), 'Property added'
    el = root[0]
    
    assert (sel := el.find('InitialExpression')) is not None, 'InitialExpression element present'
    assert sel.text == '"abc"', 'InitialExpression has surrounding quotes'
    
    # Other quoted values must be unquoted
    assert (sel := el.find('ClientName')) is not None, 'ClientName element present'
    assert sel.text == 'a b', 'ClientName has quotes stripped'


def test_doc():
    """Test property documentation"""
    
    udl = """
Class Test.Test1
{

/// Line 1
/// Line 2
Property a As %String;

}
""".lstrip()
    
    xml = convert(udl).encode()
    root = etree.fromstring(xml)
    
    assert (prop := root.find('*/Property')) is not None, 'Property element present'
    assert (el := prop.find('Description')) is not None, 'Description element present'
    assert el.text == '\nLine 1\nLine 2', 'Description is property description'
    


def test_sql_compute():
    """SqlCompute with embedded newlines and braces"""
    
    root = etree.Element("dummy")
    udl = """
Property c As %String [ InitialExpression = "}", SqlComputeCode = {Set x=4, q="}"
Set y=3
Set {*} = {a}+{b}
}, SqlComputed ];
""".lstrip()
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_property(root, stream, line, None)
    
    assert len(root), 'Property added'
    el = root[0]
    
    assert (sel := el.find('SqlComputeCode')) is not None, 'SqlComputeCode element present'
    assert sel.text == 'Set x=4, q="}"\nSet y=3\nSet {*} = {a}+{b}\n', 'SqlComputeCode has correct value'
    
    assert (sel := el.find('SqlComputed')) is not None, 'SqlComputed element present'
    assert sel.text == '1', 'SqlComputed has correct value'
    

