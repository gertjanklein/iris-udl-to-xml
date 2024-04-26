from main import convert


"""
Tests outer class syntax:
- Copyright (comment between /* */)
- Import, Include, IncludeGenerator
- Class description
"""


UDL_top_level_full = """
/* Copyright
   line 2 */

Import (Test, Test2)

Include %occInclude

IncludeGenerator %occInclude

/// 
/// Class doc
/// Line 2
/// 
Class Test.Test2
{

}
"""
XML_top_level_full = """
<?xml version='1.0' encoding='UTF-8'?>
<Export generator="IRIS" version="26">
<Class name="Test.Test2">
<Copyright>/* Copyright
   line 2 */</Copyright>
<Description>

Class doc
Line 2
</Description>
<Import>Test,Test2</Import>
<IncludeCode>%occInclude</IncludeCode>
<IncludeGenerator>%occInclude</IncludeGenerator>
</Class>
</Export>
""".lstrip()

def test_top_level_full():
    xml = convert(UDL_top_level_full)
    assert xml == XML_top_level_full, "Top-level class converted ok"



UDL_abstract = """
Class Test.Test2 [ Abstract ]
{

}
"""
XML_abstract = """
<?xml version='1.0' encoding='UTF-8'?>
<Export generator="IRIS" version="26">
<Class name="Test.Test2">
<Abstract>1</Abstract>
</Class>
</Export>
""".lstrip()

def test_abstract():
    xml = convert(UDL_abstract)
    assert xml == XML_abstract, "Abstract class converted ok"


def test_owner():
    """Tests Owner class keyword"""
    
    udl ="""
Class Test.Test4 [ Owner = {Owner1
Owner2} ]
{

}
""".lstrip()
    expect = """
<?xml version='1.0' encoding='UTF-8'?>
<Export generator="IRIS" version="26">
<Class name="Test.Test4">
<Owner>Owner1
Owner2</Owner>
</Class>
</Export>
""".lstrip()
    
    xml = convert(udl)
    assert xml == expect, "Expected Owner element present"

