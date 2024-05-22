import re
from io import StringIO

from lxml import etree

from udl2xml.util import add_el, extract, read_until
from udl2xml.split import split_nv


def handle_index(cls:etree._Element, stream:StringIO, line:str, doc:str|None):
    """Handles a index declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, ';')
    
    # First bit: get name and properties
    if not (m := re.match(r'Index ([\w%]+)\s+On\s+((?:[\w%]+)|(?:\([^[]+\)))', line, re.I)):
        raise ValueError(f"Error parsing parameter declaration around {line}")
    
    name = m[1]
    idx = add_el(cls, 'Index', '\n', 2, attr={'name':name})
    on = m[2]
    if on[0] == '(':
        on = on[1:-1].replace(', ', ',')
    add_el(idx, 'Properties', on)
    line = line[m.end():].lstrip()
    if doc:
        add_el(idx, 'Description', f"\n{doc}")
    
    # Index keywords
    if line and line[0] == '[':
        kwds = extract(line)
        for n, v in split_nv(kwds):
            if n == 'Data' and v[0] == '(':
                v = v[1:-1].replace(', ', ',')
            add_el(idx, n, v)
        line = line[len(kwds):].lstrip()
    
    if line:
        raise ValueError(f"Parse error in index {name} at around {line}")
    
    # Sort for compatibility with IRIS export
    idx[:] = sorted(idx, key=lambda el: ORDER.get(el.tag, 999))


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Description": 4,
    "Type": 5,
    "Final": 7,
    "Internal": 14,
    "Deprecated": 17,
    "Condition": 23,
    "Data": 24,
    "Extent": 25,
    "IdKey": 26,
    "PrimaryKey": 27,
    "Properties": 28,
    "SqlName": 29,
    "Unique": 31,
    "TypeClass": 33,
    "ShardKey": 34,
    "Abstract": 35,
    "CoshardWith": 36,
}

