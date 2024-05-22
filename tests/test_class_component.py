from lxml import etree

from udl2xml.main import convert

"""
Tests statements inside a class definition that are not tested
elsewhere, e.g. UDL text (single and multiline comments).
"""


def test_single_line_comment():
    """Tests a '//' single line comment"""
    
    udl ="""
Class User.Test
{
// abcde
}
""".lstrip()
    
    xml = convert(udl)
    parser = etree.XMLParser(strip_cdata=False)
    root = etree.fromstring(xml.encode(), parser=parser)
    cls = root[0]
    
    assert (el := cls.find('UDLText/Content')) is not None, 'UDLText element present'
    assert el.text == '\n// abcde\n\n', 'Comment content has correct value'
    assert '<![CDATA[' in etree.tostring(el).decode(), 'Comment content wrapped in CDATA section'


def test_multiline_comment():
    """Tests a '/* */' multiline comment"""
    
    udl ="""
Class User.Test
{
/* abcde
 */
}
""".lstrip()
    
    xml = convert(udl)
    parser = etree.XMLParser(strip_cdata=False)
    root = etree.fromstring(xml.encode(), parser=parser)
    cls = root[0]
    
    assert (el := cls.find('UDLText/Content')) is not None, 'UDLText element present'
    assert el.text == '\n/* abcde\n */\n', 'Comment content has correct value'
    assert '<![CDATA[' in etree.tostring(el).decode(), 'Comment content wrapped in CDATA section'

