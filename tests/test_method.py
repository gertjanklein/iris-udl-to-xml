from io import StringIO

from lxml import etree

from udl2xml.main import convert
from udl2xml.method import parse_parameters, handle_method
from udl2xml.util import get_line


UDL = """
ClassMethod Test(
	a As %String(MAXLEN=5),
	b) As %String(MINLEN=1) [ Abstract, CodeMode = objectgenerator, Language = objectscript, PublicList = (a, b) ]
{
	Set a = 12
	Set b = {
 }
	/*
}
{ */s x=1
	; {
	// {
	/// {
	Quit $$$OK
}
""".lstrip()

XML = """
<Method name="Test">
<Abstract>1</Abstract>
<ClassMethod>1</ClassMethod>
<CodeMode>objectgenerator</CodeMode>
<FormalSpec>a:%String(MAXLEN=5),b</FormalSpec>
<Language>objectscript</Language>
<PublicList>a,b</PublicList>
<ReturnType>%String</ReturnType>
<ReturnTypeParams>MINLEN=1</ReturnTypeParams>
<Implementation><![CDATA[
	Set a = 12
	Set b = {
 }
	/*
}
{ */s x=1
	; {
	// {
	/// {
	Quit $$$OK
]]></Implementation>
</Method>

""".lstrip()


def test_full():
    
    root = etree.Element("dummy")
    stream = StringIO(UDL)
    line = get_line(stream)
    handle_method(root, stream, line, None)
    
    assert len(root), 'Method added'
    method = root[0]
    bytes = etree.tostring(method, encoding="UTF-8", xml_declaration=False, pretty_print=False, with_tail=True)
    result = bytes.decode()
    
    assert result == XML, "Proper XML for UDL"


def test_quoted_name():
    """Test parsing of a quoted method name"""
    
    udl = """
ClassMethod "Test_a"()
{
}
}
""".lstrip()
    root = etree.Element("dummy")
    stream = StringIO(udl)
    line = get_line(stream)
    handle_method(root, stream, line, None)
    
    assert len(root), 'Method added'
    m = root[0]
    assert m.attrib.get('name','') == "Test_a"


def test_trailing_whitespace():
    """Test trailing whitespace after declaration is ignored"""
    
    udl = """
Class a
{
ClassMethod Test()
{          
}
}
""".lstrip()
    xml = convert(udl).encode()
    root = etree.fromstring(xml)
    
    assert (m := root.find('.//Method')) is not None, 'Method element present'
    assert m.attrib.get('name','') == "Test", "Method has correct name"


def test_parse_parameters():
    """Test determining FormalSpec"""
    
    parms = '(Output a As %String(MAXLEN = 5, MINLEN = "2"), ByRef b)'
    expect = '*a:%String(MAXLEN=5,MINLEN="2"),&b'
    
    result = parse_parameters(parms)
    
    assert result == expect, "Formal spec is not as expected"


def test_parse_parameters_multiline():
    """Test determining FormalSpec with multiline arguments"""
    
    parms = '(Output a As %String(MAXLEN = 5, MINLEN = "2"),\n ByRef b)'
    expect = '*a:%String(MAXLEN=5,MINLEN="2"),&b'
    
    result = parse_parameters(parms)
    
    assert result == expect, "Formal spec is not as expected"


def test_empty_default_value():
    """Test an empty parameter default value"""
    
    parms = '(Output a As %String = "")'
    expect = '*a:%String=""'
    
    result = parse_parameters(parms)
    
    assert result == expect, "Formal spec is not as expected"


def test_default_value_with_quote():
    """Test an empty parameter default value"""
    
    parms = '(Output a As %String = """", b)'
    expect = '*a:%String="""",b'
    
    result = parse_parameters(parms)
    
    assert result == expect, "Formal spec is not as expected"


def test_html():
    """Tests parsing of &html<...>"""
    
    udl = """
ClassMethod OnPage() As %Status
{
	&html<
<!doctype html>
<html>
<body>
</body>>
	Quit $$$OK
}
""".lstrip()
    root = etree.Element("dummy")
    stream = StringIO(udl)
    line = get_line(stream)
    handle_method(root, stream, line, None)
    
    assert len(root), 'Method added'


def test_json_close_brace_col1():
    """Test parsing JSON with closing brace in column 1"""
    
    udl = """
ClassMethod OnPage() As %Status
{
 Set result = {
}
}
""".lstrip()
    root = etree.Element("dummy")
    stream = StringIO(udl)
    line = get_line(stream)
    handle_method(root, stream, line, None)
    
    assert len(root), 'Method added'
    m = root[0]
    assert (el := m.find('Implementation')) is not None, 'Implementation element present'
    assert el.text == '\n Set result = {\n}\n', "Implementation is complete"


def test_method_dynobj_default_arg():
    """Test parsing of a dynamic object as parameter default"""
    
    udl = """
ClassMethod Test(Arg As %DynamicObject = {{}})
{
}
}
""".lstrip()
    root = etree.Element("dummy")
    stream = StringIO(udl)
    line = get_line(stream)
    handle_method(root, stream, line, None)
    
    assert len(root), 'Method added'
    m = root[0]
    assert (el := m.find('FormalSpec')) is not None, 'FormalSpec element present'
    assert el.text == 'Arg:%DynamicObject={{}}', "FormalSpec is correct"


def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
ClassMethod Test()
{
}
}
""".lstrip()
    
    xml = convert(udl).encode()
    root = etree.fromstring(xml)
    
    assert (doc := root.find('**/Description')) is not None, 'Description element present'
    assert doc.text == '\nThis is the documentation'
