import re
from io import StringIO

from lxml import etree

from udl2xml.util import add_el, extract, read_until
from udl2xml.split import split_nv


def handle_projection(cls:etree._Element, stream:StringIO, line:str, doc:str|None):
    """Handles a projection declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, ';')
    
    # Capture name and type
    if not (m := re.match(r'Projection\s+([\w%]+)\s+As\s+([\w%.]+)\s*', line, re.I)):
        raise ValueError(f"Parse error around {line}")
    line = line[m.end():].lstrip()
    name = m[1]
    type = m[2]
    
    prj = add_el(cls, 'Projection', '\n', 2, {'name':name})
    if doc:
        add_el(prj, 'Description', f"\n{doc}")
    add_el(prj, 'Type', type)
    
    if line and line[0] == '(':
        parms = extract(line)
        line = line[len(parms):].lstrip()
        for n, v in split_nv(parms):
            add_el(prj, 'Parameter', attr={'name': n, 'value': v})
    
    if line and line[0] == '[':
        kwds = extract(line)
        line = line[len(kwds):].lstrip()
        for n, v in split_nv(kwds):
            add_el(prj, n, v)
        
    if line:
        raise ValueError(f"Parse error starting around {line}")
    
    # Sort for compatibility with IRIS export
    prj[:] = sorted(prj, key=lambda el: ORDER.get(el.tag, 999))


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Origin": 2,
    "Description": 4,
    "Type": 5,
    "Notinheritable": 9,
    "Sequencenumber": 11,
    "Keyworderror": 12,
    "Keywordmodified": 13,
    "Internal": 14,
    "Deprecated": 17,
}

