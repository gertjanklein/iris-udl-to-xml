import re
from io import StringIO

from lxml import etree

from udl2xml.util import add_el, read_until, get_line


def handle_storage(cls:etree._Element, stream:StringIO, line:str, doc:str|None):
    """Handles a storage declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, '{')
    
    # Get name
    if not (m := re.match(r'Storage\s+(\S+)\s*', line, re.I)):
        raise ValueError(f"Error parsing storage declaration around {line}")
    name = m[1]
    
    # Create element
    stg = add_el(cls, 'Storage', '\n', 2, {'name':name})
    if doc:
        add_el(stg, 'Description', f"\n{doc}\n")
    
    lines = []
    while True:
        # Single closing brace ends the storage; it can't be part of the
        # contents. (?)
        line = get_line(stream)
        if line == '}':
            break
        lines.append(line)
    
    # Storage can contain multiple elements, not wrapped in a single root.
    # To get at them, wrap these XML elements inside a temporary root.
    storage = f"<root___temp>{'\n'.join(lines)}\n</root___temp>"
    root = etree.fromstring(storage)
    
    # Sort for compatibility with IRIS export. In UDL, the elements are ordered
    # alphabetically, but in an XML export they are ordered according to ^oddCOM.
    root[:] = sorted(root, key=lambda el: ORDER.get(el.tag, 999))
    for el in root:
        # Property subelements are also sorted differently
        if el.tag == 'Property':
            el[:] = sorted(el, key=lambda el: ORDER_PROP.get(el.tag, 999))
    
    # Add subelements of the temporary root to our Storage element
    for el in root:
        stg.append(el)


ORDER = {
    "Description": 4,
    "Type": 5,
    "Final": 7,
    "Internal": 14,
    "Deprecated": 17,
    "DataLocation": 21,
    "DefaultData": 22,
    "IdExpression": 23,
    "IdLocation": 24,
    "IndexLocation": 25,
    "SqlChildSub": 27,
    "SqlIdExpression": 28,
    "SqlRowIdName": 29,
    "SqlRowIdProperty": 30,
    "SqlTableNumber": 31,
    "State": 32,
    "StreamLocation": 33,
    "VersionLocation": 35,
    "CounterLocation": 36,
    "IdFunction": 37,
    "ExtentLocation": 38,
    "ExtentSize": 34,
    "Sharded": 40,
}

ORDER_PROP = {
    "Selectivity": 21,
    "StreamLocation": 22,
    "ChildExtentSize": 23,
    "OutlierSelectivity": 24,
    "BiasQueriesAsOutlier": 25,
    "AverageFieldSize": 26,
    "ChildBlockCount": 27,
    "Histogram": 28,
}

