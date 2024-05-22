import re
from io import StringIO

from lxml import etree

from udl2xml.util import add_el, extract, get_line, unquote, read_until
from udl2xml.split import split_nv
from udl2xml.method import parse_parameters


def handle_query(cls:etree._Element, stream:StringIO, line:str, doc:str|None):
    """Handles a query declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, '{')
    
    # First, get the name
    if not (m := re.match(r'Query\s+([\w.%]+)\(', line, re.I)):
        raise ValueError(f"Parse error around {line}")
    name = m[1]
    line = line[m.end(1):]
    
    qry = add_el(cls, 'Query', '\n', 2, {'name':name})
    if doc:
        add_el(qry, 'Description', f"\n{doc}")
    
    parms = extract(line)
    line = line[len(parms):].lstrip()
    spec = parse_parameters(parms)
    if spec:
        add_el(qry, 'FormalSpec', spec)
    
    # Determine the type
    if not (m := re.match(r'As\s+([\w.%]+)\b', line, re.I)):
        raise ValueError(f"Parse error in query {name} definition around {line}")
    type = m[1]
    line = line[m.end():].lstrip()
    add_el(qry, 'Type', type)
    
    # Query class parameters (ROWSPEC etc.)
    if line and line[0] == '(':
        parms = extract(line)
        line = line[len(parms):].lstrip()
        for n, v in split_nv(parms):
            if v and v[0] == '"':
                v = unquote(v)
            add_el(qry, 'Parameter', attr={'name':n, 'value':v})
    
    # Keywords ([ Final ] etc.)
    if line and line[0] == '[':
        kwds = extract(line)
        for n, v in split_nv(kwds):
            add_el(qry, n, v)
    
    # Get the implementation. %Query-type queries normally don't have
    # any content, but appear to support SQL syntax. %SQLQuery-type
    # queries contain a SQL statement.
    impl = get_implementation_sql(stream, name)
    if impl:
        add_el(qry, 'SqlQuery', impl)
    
    # Sort for compatibility with IRIS export
    qry[:] = sorted(qry, key=lambda el: ORDER.get(el.tag, 999))


def get_implementation_sql(stream:StringIO, name:str) ->str:
    """Returns the implementation for a code-type query"""
    
    lines = []
    while True:
        # Single closing brace ends the query implementation; it can't be
        # part of the contents. (?)
        line = get_line(stream)
        if line == '}':
            break
        lines.append(line)
    
    return '\n'.join(lines)


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Description": 4,
    "Type": 5,
    "Final": 7,
    "Internal": 14,
    "Deprecated": 17,
    "FormalSpec": 24,
    "Private": 26,
    "SqlName": 27,
    "SqlProc": 28,
    "SqlQuery": 29,
    "SqlView": 30,
    "SqlViewName": 31,
    "WebMethod": 33,
    "SoapBindingStyle": 35,
    "SoapBodyUse": 36,
    "SoapNameSpace": 37,
    "Cardinality": 40,
    "ClientName": 41,
}

