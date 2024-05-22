import re
from io import StringIO

from lxml import etree

from udl2xml.util import add_el, extract, read_until
from udl2xml.split import split_nv
from udl2xml.implementation import get_implementation


def handle_trigger(cls:etree._Element, stream:StringIO, line:str, doc:str|None, lang:str='objectscript'):
    """Handles a trigger declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, '{')
    
    # Name
    if not (m := re.match(r'Trigger\s+([\w%]+)\s*', line, re.I)):
        raise ValueError(f"Parse error around {line}")
    line = line[m.end():].lstrip()
    name = m[1]
    
    trg = add_el(cls, 'Trigger', '\n', 2, {'name':name})
    if doc:
        add_el(trg, 'Description', f"\n{doc}")
    
    if line and line[0] == '[':
        kwds = extract(line)
        line = line[len(kwds):].lstrip()
        for n, v in split_nv(kwds):
            if n == 'Language':
                lang = v
            add_el(trg, n, v)

    if line:
        raise ValueError(f"Parse error starting around {line}")
    
    # Get trigger implementation
    impl = get_implementation(stream, lang, name)
    if impl:
        add_el(trg, 'Code', impl)
    
    # Sort for compatibility with IRIS export
    trg[:] = sorted(trg, key=lambda el: ORDER.get(el.tag, 999))


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Description": 4,
    "Final": 7,
    "Internal": 14,
    "Deprecated": 17,
    "Code": 21,
    "Event": 22,
    "Order": 23,
    "SqlName": 24,
    "Time": 25,
    "Foreach": 26,
    "Language": 27,
    "UpdateColumnList": 28,
    "NewTable": 29,
    "OldTable": 30,
    "CodeMode": 31,
}

