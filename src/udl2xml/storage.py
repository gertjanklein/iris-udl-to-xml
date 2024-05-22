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
    # Add subelements of the temporary root to our Storage element
    for el in root:
        stg.append(el)
