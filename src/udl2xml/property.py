import re
from io import StringIO

from lxml import etree

from udl2xml.util import add_el, unquote, extract, read_until
from udl2xml.split import split_nv


def handle_property(cls:etree._Element, stream:StringIO, line:str, doc:str|None):
    """Handles a property declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, ';')
    
    # First determine prop/rel and name
    if not (m := re.match(r'(Property|Relationship)\s+((?:[\w%]+)|(?:"(""|[^"])+)")', line, re.I)):
        raise ValueError(f"Parse error around {line}")
    name = m[2]
    if name[0] == '"':
        name = unquote(name)
    is_rel = m[1].title() == 'Relationship'
    line = line[m.end(2):].lstrip()
    
    # Determine type
    if m := re.match(r'(?i)As\s+(?:(list|array) Of\s+)?([\w%.]+)', line):
        collection = m[1].lower() if m[1] is not None else ''
        type = m[2]
        line = line[m.end(2):].lstrip()
    else:
        collection = type = ''
    
    prop = add_el(cls, 'Property', '\n', 2, {'name':name})
    if type != '':
        add_el(prop, 'Type', type)
    if not doc is None:
        add_el(prop, 'Description', '\n'+doc)
    if not collection == '':
        add_el(prop, 'Collection', collection)
    if is_rel:
        add_el(prop, 'Relationship', '1')
    
    # First, check for property parameters
    if line and line[0] == '(':
        parms = extract(line)
        line = line[len(parms):].strip()
        
        for n, v in split_nv(parms):
            attr = { 'name': n }
            if v[0] == '"':
                v = unquote(v)
            # Value attribute not present if empty
            if v != "":
                attr['value'] = v
            add_el(prop, 'Parameter', attr=attr)
    
    if line:
        if line[0] == '[':
            # We expect this to run to the end of the property declaration
            if not line.endswith(']'):
                raise ValueError(f"Parse error starting around {line}")
            
            for n, v in split_nv(line, '{['):
                if v[0] == '"' and n != 'InitialExpression':
                    v = unquote(v)
                add_el(prop, n, v)
        else:
            raise ValueError(f"Parse error starting around {line}")
    
    # Sort for compatibility with IRIS export
    prop[:] = sorted(prop, key=lambda el: ORDER.get(el.tag, 999))
    


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Description": 4,
    "Type": 5,
    "Final": 7,
    "Internal": 14,
    "Deprecated": 17,
    "Calculated": 23,
    "Cardinality": 24,
    "ClientName": 26,
    "Collection": 27,
    "InitialExpression": 31,
    "Inverse": 32,
    "MultiDimensional": 33,
    "Private": 35,
    "Relationship": 36,
    "Required": 37,
    "SqlColumnNumber": 43,
    "SqlComputeCode": 44,
    "SqlComputed": 45,
    "SqlComputeOnChange": 46,
    "SqlFieldName": 47,
    "SqlListDelimiter": 48,
    "SqlListType": 49,
    "Transient": 51,
    "Readonly": 52,
    "Identity": 56,
    "ServerOnly": 57,
    "Aliases": 58,
    "OnDelete": 59,
}

