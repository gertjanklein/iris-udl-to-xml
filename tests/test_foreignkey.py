from io import StringIO

from lxml import etree

from udl2xml.main import convert
from udl2xml.util import get_line
from udl2xml.foreignkey import handle_foreignkey


def test_no_index():
    """Test foreign key without index specified"""
    
    udl = "ForeignKey FK1(A) References Test.A();"
    fk = call_handler(udl)
    assert fk.find('ReferencedKey') is None, 'ReferencedKey element absent'


def test_no_prop_with_quote():
    """Test foreign key with a quoted property"""
    
    udl = 'ForeignKey FK1(A,"b_a") References Test.A(IDKEY);'
    fk = call_handler(udl)
    assert (el := fk.find('Properties')) is not None, 'Properties element present'
    assert el.text == 'A,"b_a"'


def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
ForeignKey FK1(A) References Test.A(IDKEY) [ NoCheck ];
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
    
    handle_foreignkey(root, stream, line, None)
    
    assert len(root) == 1, 'Element added'
    return root[0]

