import re
from io import StringIO

from io import StringIO

from lxml import etree

from util import add_el, extract, read_until
from split import split_nv


def handle_foreignkey(cls:etree._Element, stream:StringIO, line:str, doc:str|None):
    """Handles a foreignkey declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, ';')
    
    # Capture key name, properties, referenced class, and index name
    if not (m := re.match(r'ForeignKey\s+([^(]+)\(([^)]+)\)\s+References\s+([^(]+)\(([^)]*)\)', line, re.I)):
        raise ValueError(f"Parse error around {line}")
    name = m[1]
    props = m[2]
    ref_cls = m[3]
    idx = m[4]
    line = line[m.end():].lstrip()
    
    # Create element
    fk = add_el(cls, 'ForeignKey', '\n', 2, {'name':name})
    if doc:
        add_el(fk, 'Description', f"\n{doc}")
    
    # Add stuff catured above. Referenced key is optional.
    add_el(fk, 'Properties', props)
    add_el(fk, 'ReferencedClass', ref_cls)
    if idx:
        add_el(fk, 'ReferencedKey', idx)
    
    # Add keywords, if any
    if line and line[0] == '[':
        kwds = extract(line)
        line = line[len(kwds):].lstrip()
        for n, v in split_nv(kwds):
            add_el(fk, n, v)
    
    if line:
        raise ValueError(f"Parsing error in parameter {name} around {line}")
    
    # Sort for compatibility with IRIS export
    fk[:] = sorted(fk, key=lambda el: ORDER.get(el.tag, 999))


ORDER = {
    "Description": 4,
    "Final": 7,
    "Internal": 14,
    "Deprecated": 17,
    "OnDelete": 21,
    "OnUpdate": 22,
    "Properties": 23,
    "ReferencedClass": 24,
    "ReferencedKey": 25,
    "SqlName": 26,
    "NoCheck": 27,
}

