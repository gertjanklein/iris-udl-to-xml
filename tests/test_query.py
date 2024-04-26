from io import StringIO

from lxml import etree

from main import convert
from util import get_line
from query import handle_query


def test_sql_query():
    """Tests parsing of an SQL-type query"""
    
    udl = """
Query Q1Sql(SearchA As %String) As %SQLQuery(COMPILEMODE = "DYNAMIC", CONTAINID = 1) [ Final, WebMethod ]
{
SELECT %ID FROM Query
}
""".lstrip()
    qry = call_handler(udl)
    
    assert (el := qry.find('Type')) is not None, 'Type element present'
    assert el.text == '%SQLQuery', "Type has correct value"
    
    assert (el := qry.find('Final')) is not None, 'Final element present'
    assert el.text == '1', "Final has correct value"
    
    assert (el := qry.find('FormalSpec')) is not None, 'FormalSpec element present'
    assert el.text == 'SearchA:%String', "FormalSpec has correct value"
    
    assert (el := qry.find('SqlQuery')) is not None, 'SqlQuery element present'
    assert el.text == 'SELECT %ID FROM Query', "SqlQuery has correct value"
    
    assert (el := qry.find('WebMethod')) is not None, 'WebMethod element present'
    assert el.text == '1', "WebMethod has correct value"
    
    assert (lst := qry.xpath("./Parameter[@name='COMPILEMODE']")), 'Parameter for compile mode present'
    assert lst[0].attrib.get('value') == 'DYNAMIC', "Parameter for compile mode has correct value"
    
    assert (lst := qry.xpath("./Parameter[@name='CONTAINID']")), 'Parameter for compile mode present'
    assert lst[0].attrib.get('value') == '1', "Parameter for compile mode has correct value"


def test_sqlproc():
    """Tests handling of SqlProc keyword"""
    
    udl = """
Query Query() As %SQLQuery [ SqlProc ]
{
}
""".lstrip()
    qry = call_handler(udl)
    
    assert (el := qry.find('Type')) is not None, 'Type element present'
    assert el.text == '%SQLQuery', "Type has correct value"
    
    assert (el := qry.find('SqlProc')) is not None, 'SqlProc element present'
    assert el.text == '1', "SqlProc has correct value"
    
    

def test_code_query():
    """Tests parsing of an code-type query"""
    
    udl = """
Query Q2Code(SearchB As %String) As %Query(ROWSPEC = "a:%String,b:%String") [ Internal ]
{
}
""".lstrip()
    qry = call_handler(udl)
    
    assert (el := qry.find('Type')) is not None, 'Type element present'
    assert el.text == '%Query', "Type has correct value"
    
    assert (el := qry.find('Internal')) is not None, 'Internal element present'
    assert el.text == '1', "Internal has correct value"
    
    assert (el := qry.find('FormalSpec')) is not None, 'FormalSpec element present'
    assert el.text == 'SearchB:%String', "FormalSpec has correct value"
    
    assert (lst := qry.xpath("./Parameter[@name='ROWSPEC']")), 'Parameter for rowspec present'
    assert lst[0].attrib.get('value') == 'a:%String,b:%String', "Parameter for rowspec has correct value"


def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
Query Q2Code(SearchB As %String) As %Query(ROWSPEC = "a:%String,b:%String") [ Internal ]
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
    
    handle_query(root, stream, line, None)
    
    assert len(root) == 1, 'Element added'
    return root[0]

