from io import StringIO

from lxml import etree

from main import convert
from util import get_line
from xdata import handle_xdata


def test_type_text():
    """Type text/plain xdata"""
    
    root = etree.Element("dummy")
    udl = """
XData Text [ MimeType = text/plain ]
{
abc
def
}
""".lstrip()
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_xdata(root, stream, line, None)
    
    assert len(root), 'XData added'
    xdata = root[0]
    assert xdata.tag == 'XData', 'XData has correct tag'
    assert xdata.attrib.get('name') == 'Text', 'XData has correct name'
    
    assert (sel := xdata.find('MimeType')) is not None, 'MimeType element present'
    assert sel.text == 'text/plain', 'MimeType has correct value'
    
    assert (sel := xdata.find('Data')) is not None, 'Data element present'
    assert sel.text == '\nabc\ndef\n', 'Data has correct value'


def test_type_json():
    """Type application/json xdata"""
    
    root = etree.Element("dummy")
    udl = """
XData JSON [ MimeType = application/json ]
{
{"a":"b}",
 "c":{}}
}
""".lstrip()
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_xdata(root, stream, line, None)
    
    assert len(root), 'XData added'
    xdata = root[0]
    assert xdata.tag == 'XData', 'XData has correct tag'
    assert xdata.attrib.get('name') == 'JSON', 'XData has correct name'
    
    assert (sel := xdata.find('MimeType')) is not None, 'MimeType element present'
    assert sel.text == 'application/json', 'MimeType has correct value'
    
    assert (sel := xdata.find('Data')) is not None, 'Data element present'
    assert sel.text == '\n{"a":"b}",\n "c":{}}\n', 'Data has correct value'


def test_type_xml():
    """Type text/xml xdata"""
    
    root = etree.Element("dummy")
    udl = """
XData XML [ MimeType = text/xml ]
{
<?xml version='1.0' encoding='UTF-8'?><root attrib="<y>">
}
</root>
}
""".lstrip()
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_xdata(root, stream, line, None)
    
    assert len(root), 'XData added'
    xdata = root[0]
    assert xdata.tag == 'XData', 'XData has correct tag'
    assert xdata.attrib.get('name') == 'XML', 'XData has correct name'
    
    assert (sel := xdata.find('MimeType')) is not None, 'MimeType element present'
    assert sel.text == 'text/xml', 'MimeType has correct value'
    
    assert (sel := xdata.find('Data')) is not None, 'Data element present'
    assert sel.text == '\n<?xml version=\'1.0\' encoding=\'UTF-8\'?><root attrib="<y>">\n}\n</root>\n', 'Data has correct value'


def test_xml_cdata():
    """Tests that XML is wrapped in CDATA"""
    
    root = etree.Element("dummy")
    udl = """
XData XML
{
<root>Something</root>
}
""".lstrip()
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_xdata(root, stream, line, None)
    
    assert len(root), 'XData added'
    assert (data := root[0].find('Data')) is not None, 'Data element present'
    txt = etree.tostring(data).decode()
    assert txt == '<Data><![CDATA[<root>Something</root>\n]]></Data>\n', "Data wrapped in CDATA block"


def test_xml_embedded_cdata():
    """Tests handling of 'embedded' CDATA"""
    
    # lxml does not support CDATA with 'escaped' CDATA blocks within. We
    # use a patched version that allows (and properly escapes) this.
    
    root = etree.Element("dummy")
    udl = """
XData XML
{
<root><![CDATA[Some&thing]]></root>
}
""".lstrip()
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_xdata(root, stream, line, None)
    
    assert len(root), 'XData added'
    assert (data := root[0].find('Data')) is not None, 'Data element present'
    txt = etree.tostring(data).decode()
    assert txt == '<Data><![CDATA[<root><![CDATA[Some&thing]]]]><![CDATA[></root>\n]]></Data>\n', "Embedded CDATA escaped"


def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
XData x
{
}
}
""".lstrip()
    
    xml = convert(udl).encode()
    root = etree.fromstring(xml)
    
    assert (doc := root.find('**/Description')) is not None, 'Description element present'
    assert doc.text == '\nThis is the documentation'

