from io import StringIO

from lxml import etree

from main import convert
from util import get_line
from storage import handle_storage


def test_empty_serial():
    """Test conversion of no-properties serial storage"""
    
    udl = """
Storage Default
{
<StreamLocation>^Test.BS</StreamLocation>
<Type>%Storage.Serial</Type>
}
""".lstrip()
    stg = call_handler(udl)
    assert stg.attrib.get('name', '') == 'Default', "Storage name in attribute"
    assert stg.find('StreamLocation') is not None, 'StreamLocation element present'
    assert stg.find('Type') is not None, 'Type element present'


def test_empty_persistent():
    """Test conversion of no-properties persistent storage"""
    
    udl = """
Storage Default
{
<Data name="ADefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
</Data>
<DataLocation>^Test.AD</DataLocation>
<DefaultData>ADefaultData</DefaultData>
<IdLocation>^Test.AD</IdLocation>
<IndexLocation>^Test.AI</IndexLocation>
<StreamLocation>^Test.AS</StreamLocation>
<Type>%Storage.Persistent</Type>
}
""".lstrip()
    stg = call_handler(udl)
    assert stg.attrib.get('name', '') == 'Default', "Storage name in attribute"
    assert (data := stg.find('Data')) is not None, 'Data element present'
    assert (value := data.find('Value')) is not None, 'Value element present'
    assert value.attrib.get('name', '') == '1', 'Value has proper name attribute'
    assert value.find('Value') is not None, 'Value has nexted Value element'
    assert stg.find('DataLocation') is not None, 'DataLocation element present'
    assert stg.find('DefaultData') is not None, 'DefaultData element present'
    assert stg.find('IdLocation') is not None, 'IdLocation element present'
    assert stg.find('IndexLocation') is not None, 'IndexLocation element present'
    assert stg.find('StreamLocation') is not None, 'StreamLocation element present'
    assert stg.find('Type') is not None, 'Type element present'


def test_doc():
    """Test that documentation is added"""
    
    udl = """
Class a.b
{
/// This is the documentation
Storage Default
{
<StreamLocation>^Test.BS</StreamLocation>
<Type>%Storage.Serial</Type>
}
}
""".lstrip()
    
    xml = convert(udl).encode()
    root = etree.fromstring(xml)
    
    assert (doc := root.find('**/Description')) is not None, 'Description element present'
    assert doc.text == '\nThis is the documentation\n'


def call_handler(udl:str) -> etree._Element:
    """Helper to call the handler method"""
    
    root = etree.Element("dummy")
    root.text = '\n'
    stream = StringIO(udl)
    line = get_line(stream)
    
    handle_storage(root, stream, line, None)
    
    assert len(root) == 1, 'Element added'
    return root[0]

