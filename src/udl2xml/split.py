from typing import Generator
import re

from udl2xml.util import unquote, get_quoted_string, extract


"""
Splits comma-separated lists of name=value, as present in e.g. the
property parameter and keyword lists. Supports quoted values,
code values (in curly braces), lists (parenthesis), etc.
"""


def split_nv(data:str, strip_delim='') -> Generator[tuple[str, str], None, None]:
    """Split the list into name, value pairs"""
    
    # Check we have known and consistent delimiters
    first = data[0]
    last = data[-1]
    assert first+last in ('[]', '()'), f"Inconsistent delimiters: {first+last}"
    
    # Remove them
    data = data[1:-1].strip()
    
    while len(data):
        # Booleans: [Not ]Something
        if m := re.match(r'(Not )?(\w+)\s*(,|$)', data):
            name = m.group(2)
            value = '1' if m.group(1) is None else '0'
            data = data[m.end(3):].lstrip()
            yield name, value
            continue
        
        # Something = ...
        elif m := re.match(r'([\w%]+)\s*(=)', data):
            name = m.group(1)
            data = data[m.end(2):].lstrip()
        
        else:
            raise ValueError(f"Error parsing expression: {data}")
        
        # We've got the name; we need a value now. Determine delimiter (if any)
        delim = data[0]
        
        if delim == '"':
            value = get_quoted_string(data)
            data = data[len(value)+1:].lstrip()
            if '"' in strip_delim:
                value = unquote(value)
            
        elif delim in '({':
            value = extract(data)
            data = data[len(value):].lstrip()
            
            if value[0] in strip_delim:
                value = value[1:-1]
            
            if not (m := re.match(r'\s*(,|$)', data)):
                raise ValueError(f"Parse error starting at {data}")
            
            data = data[m.end(1)+1:].lstrip()
        
        else:
            # Not a delimited value
            if not (m := re.match(r'([\w./]+)\s*(,|$)', data)):
                raise ValueError(f"Can't determine value in {data}")
            value = m.group(1)
            data = data[m.end(2):].lstrip()
            
        yield name, value

