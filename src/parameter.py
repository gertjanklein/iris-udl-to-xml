import re
from io import StringIO

from lxml import etree

from util import add_el, extract, unquote, read_until
from split import split_nv


def handle_parameter(cls:etree._Element, stream:StringIO, line:str, doc:str|None):
    """Handles a parameter declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, ';')
    
    # First bit: get name and optional type
    if not (m := re.match(r'Parameter ([\w%]+)(?:\s+As\s+([\w%.]+))?', line, re.I)):
        raise ValueError(f"Error parsing parameter declaration around {line}")
    
    name = m[1]
    type = m[2]
    line = line[m.end(0):].lstrip()
    
    parm = add_el(cls, 'Parameter', '\n', 2, {'name':name})
    if type:
        add_el(parm, 'Type', type)
    if doc:
        add_el(parm, 'Description', f"\n{doc}")
    
    if line and line[0] == '[':
        kwds = extract(line)
        line = line[len(kwds):].lstrip()
        for n, v in split_nv(kwds):
            if v and v[0] == '"':
                v = unquote(v)
            add_el(parm, n, v)
    
    if line:
        if not (m := re.match(r'=\s+(.+)', line)):
            raise ValueError(f"Error parsing parameter declaration around {line}")
        default = m[1]
        if default[0] == '{':
            add_el(parm, 'Expression', extract(default)[1:-1])
        else:
            if default[0] == '"':
                default = unquote(default)
            add_el(parm, 'Default', default)
        line = line[m.end(0):]
    
    if line:
        raise ValueError(f"Parsing error in parameter {name} around {line}")
    
    # Sort for compatibility with IRIS export
    parm[:] = sorted(parm, key=lambda el: ORDER.get(el.tag, 999))


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Description": 4,
    "Type": 5,
    "Final": 7,
    "Internal": 14,
    "Deprecated": 17,
    "Constraint": 21,
    "Default": 22,
    "Flags": 23,
    "Abstract": 24,
    "Expression": 25,
    "Encoded": 27,
}
