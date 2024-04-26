from io import StringIO

from lxml import etree

from main import convert
from util import get_line
from parameter import handle_parameter


def test_bare():
    """Empty parameter"""
    
    root = etree.Element("dummy")
    udl = 'Parameter a;'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_parameter(root, stream, line, None)
    
    assert len(root), 'Parameter added'
    parm = root[0]
    assert parm.tag == 'Parameter', 'Parameter has correct tag'
    assert parm.attrib.get('name') == 'a', 'Parameter has correct name'
    
    assert len(parm) == 0, 'No subelements present'


def test_trailing_whitespace():
    """Test trailing whitespace after declaration is ignored"""
    
    root = etree.Element("dummy")
    udl = 'Parameter a;'
    stream = StringIO(udl)
    line = get_line(stream)
    
    # If the trailing whitespace is not ignored, this raises a parse error
    handle_parameter(root, stream, line, None)
    
    assert len(root), 'Parameter added'
    assert root[0].tag == 'Parameter', 'Parameter has correct tag'


def test_type():
    """Test parameter type correctly handled"""
    
    root = etree.Element("dummy")
    udl = 'Parameter a As INTEGER;'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_parameter(root, stream, line, None)
    
    assert len(root), 'Parameter added'
    parm = root[0]
    assert parm.tag == 'Parameter', 'Parameter has correct tag'
    assert parm.attrib.get('name') == 'a', 'Parameter has correct name'
    
    assert (sel := parm.find('Type')) is not None, 'Type element present'
    assert sel.text == 'INTEGER', 'Type has correct value'


def test_default():
    """Test parameter value correctly handled"""
    
    root = etree.Element("dummy")
    udl = 'Parameter a = "abc";'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_parameter(root, stream, line, None)
    
    assert len(root), 'Parameter added'
    parm = root[0]
    assert len(parm) == 1, "Parameter has one subelement"
    assert parm.tag == 'Parameter', 'Parameter has correct tag'
    assert parm.attrib.get('name') == 'a', 'Parameter has correct name'
    
    assert (sel := parm.find('Default')) is not None, 'Default element present'
    assert sel.text == 'abc', 'Default has correct value'


def test_default_expr():
    """Test parameter value expression correctly handled"""
    
    root = etree.Element("dummy")
    udl = 'Parameter a = {$zh};'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_parameter(root, stream, line, None)
    
    assert len(root), 'Parameter added'
    parm = root[0]
    assert len(parm) == 1, "Parameter has one subelement"
    assert parm.tag == 'Parameter', 'Parameter has correct tag'
    assert parm.attrib.get('name') == 'a', 'Parameter has correct name'
    
    assert (sel := parm.find('Expression')) is not None, 'Expression element present'
    assert sel.text == '$zh', 'Expression has correct value'


def test_keywords():
    """Test parameter keywords correctly handled"""
    
    root = etree.Element("dummy")
    udl = 'Parameter a [ Abstract, Constraint = "abc,def", Flags = ENUM ];'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_parameter(root, stream, line, None)
    
    assert len(root), 'Parameter added'
    parm = root[0]
    assert len(parm) == 3, "Parameter has 3 subelements"
    assert parm.tag == 'Parameter', 'Parameter has correct tag'
    assert parm.attrib.get('name') == 'a', 'Parameter has correct name'
    
    assert (sel := parm.find('Abstract')) is not None, 'Abstract element present'
    assert sel.text == '1', 'Abstract has correct value'
    
    assert (sel := parm.find('Constraint')) is not None, 'Constraint element present'
    assert sel.text == 'abc,def', 'Constraint has correct value'
    
    assert (sel := parm.find('Flags')) is not None, 'Flags element present'
    assert sel.text == 'ENUM', 'Flags has correct value'


def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
Parameter x;
}
""".lstrip()
    
    xml = convert(udl).encode()
    root = etree.fromstring(xml)
    
    assert (doc := root.find('**/Description')) is not None, 'Description element present'
    assert doc.text == '\nThis is the documentation'

