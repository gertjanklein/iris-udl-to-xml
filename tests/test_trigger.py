from io import StringIO

from lxml import etree

from main import convert
from util import get_line
from trigger import handle_trigger


def test_basic():
    """Test basic fields"""
    
    udl = """
Trigger T [ Event = INSERT ]
{
}
""".lstrip()
    trg = call_handler(udl)
    
    assert trg.attrib.get('name') == 'T', "Trigger name present"
    assert (el := trg.find('Event')) is not None, "Event element present"
    assert el.text == 'INSERT', "Event has correct value"
    
    assert trg.find('Code') is None, "No code element present"


def test_impl():
    """Test implementation copied"""
    
    udl = """
Trigger T [ Event = INSERT ]
{
 Set a = b
 Do ..Something()
}
""".lstrip()
    trg = call_handler(udl)
    
    assert (el := trg.find('Code')) is not None, "Code element present"
    assert el.text == ' Set a = b\n Do ..Something()'


def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
Trigger T2 [ Event = DELETE ]
{
}
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
    
    handle_trigger(root, stream, line, None)
    
    assert len(root) == 1, 'Element added'
    return root[0]

