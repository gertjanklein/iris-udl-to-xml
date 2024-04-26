from io import StringIO

from lxml import etree
from lxml.etree import CDATA


def get_line(stream:StringIO) -> str:
    """Returns a line from stream, removing the line terminator"""
    
    line = stream.readline()
    if line == '':
        raise ValueError("Unexpected end of input")
    if line[-1] == '\n':
        line = line[:-1]
    return line


def add_el(to:etree._Element, name:str, text:str|None=None, tailcount:int=1, attr:dict[str, str]={}):
    """Adds a subelement to an existing element"""
    
    el = etree.SubElement(to, name)
    if text is not None:
        el.text = text
    el.tail = '\n' * tailcount
    for n, v in attr.items():
        el.attrib[n] = v
    return el


def add_comment(cls, data):
    """Adds a class comment (UDL text)"""
    
    el = etree.SubElement(cls, 'UDLText')
    el.attrib['name'] = 'T'
    el.text = '\n'
    el.tail = '\n\n'
    el = add_el(el, 'Content', CDATA(data))


def read_until(stream:StringIO, line:str, terminator:str) -> str:
    """Read stream until terminator is found; removes it"""
    
    # Read until a line that ends with terminator is found.
    # Ignore any trailing whitespace
    while not line.rstrip().endswith(terminator):
        line += '\n' + get_line(stream)
    line = line.rstrip().removesuffix(terminator)
    
    return line


def unquote(data:str) -> str:
    """Searches for the end quote, de-doubles quotes"""
    
    value = ''
    i = 1
    while i < len(data):
        c = data[i]
        i += 1
        if c != '"':
            value += c
        elif i < len(data) and data[i] == '"':
            value += c
            i += 1
        else:
            break
    
    return value


def get_quoted_string(data:str) -> str:
    """Returns a quoted string without removing quotes"""
    
    assert data[0] == '"', "Data does not start with a quote"
    
    value = '"'
    i = 1
    q = 0
    while i < len(data):
        c = data[i]
        value += c
        i += 1
        if c != '"':
            continue
        elif i == len(data):
            if q:
                raise ValueError(f"Unmatched quotes in {data}")
            return value
        elif q:
            q = 0
        elif data[i] != '"':
            return value
        else:
            q = 1
        
    raise ValueError(f"End of string scanning for close quote in {data}")


def get_word(data:str, add:str='') -> str:
    """Returns the word, ending at space or eol
    
    A 'word' consists of alphanumeric characters; additional characters
    to allow can be passed in parameter 'add'.
    """
    
    value = data[0]
    i = 1
    while i < len(data):
        c = data[i]
        if c.isalpha() or c.isnumeric() or c in add:
            value += c
            i += 1
        else:
            break
    
    return value


def find_closing_brace(data:str) -> int:
    """Returns the position of the closing brace in data"""
    
    i = 1
    depth = 0
    state = ''
    while i < len(data):
        c = data[i]
        i += 1
        if state == '':
            if c == '{':
                depth += 1
            if c == '}':
                if not depth:
                    return i
                depth -= 1
            if c == '"':
                state = 'inq'
        elif state == 'inq':
            if c == '"':
                if i < len(data) and data[i] == '"':
                    i += 1
                else:
                    state = ''
    
    raise ValueError(f"Error finding matching closing brace in {data}")


def find_closing(data:str, char:str) -> int:
    """Find closing char, ignoring anything in quotes"""
    
    i = 1
    state = ''
    while i < len(data):
        c = data[i]
        i += 1
        if state == '':
            if c == char:
                return i
            if c == '"':
                state = 'inq'
        elif state == 'inq':
            if c == '"':
                if i < len(data) and data[i] == '"':
                    i += 1
                else:
                    state = ''
    
    raise ValueError(f"Error finding matching closing brace in {data}")


def extract(data:str) -> str:
    """Extracts data delimited by ()/[]/{}
    
    Returns the delimited string, including delimiters. Supports nesting
    (the same) delimiter; e.g., '(())' returns '(())', not '(()'.
    Ignores nested delimiters if they are inside quotes: '(")")' returns
    '(")")', not '(")'. Quotes are assumed to be escaped by doubling
    them: '("")"")' returns '("")'.
    """
    
    # Determine open and closing brace/parenthesis
    open = data[0]
    close = { '(': ')', '[': ']', '{': '}' }.get(open)
    if not close:
        raise ValueError(f"Unrecognised delimiter {open}")
    
    i = 1
    depth = 0
    state = ''
    while i < len(data):
        c = data[i]
        i += 1
        if state == '':
            if c == open:
                depth += 1
            elif c == close:
                if not depth:
                    return data[:i]
                depth -= 1
            elif c == '"':
                state = 'inq'
            elif c == '{':
                # Curly braces can contain bare ']', handle separately
                tmp = extract(data[i-1:])
                i += len(tmp)-1
        elif state == 'inq':
            if c == '"':
                if i < len(data) and data[i] == '"':
                    i += 1
                else:
                    state = ''
    
    raise ValueError(f"Error finding matching closing '{close}' in {data}")


def startswithi(data:str, sw:str|tuple) -> bool:
    """Case-insensitive startswith"""
    
    data = data.lower()
    if isinstance(sw, str):
        return data.startswith(sw.lower())
    for s in sw:
        if data.startswith(s.lower()):
            return True
    return False


