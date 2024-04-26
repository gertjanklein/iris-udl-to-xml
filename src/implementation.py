import re
from io import StringIO

from util import get_line


"""
Parses and returns implementations enclosed in curly braces, like method
and trigger implementations and XData. The type of code/data has to be
known to be able to parse for the closing curly brace, and is passed in
parameter type. It can be a single value like 'objectscript', or a mime
type like 'text/xml'.

The data passed in stream is expected to not contain the opening curly
brace. Data is consumed here up to and including the closing curly
brace.

XData mime types known in Studio (not all of these are implemented
here):

. text/plain
. application/json
. application/xml
. text/xml
. application/python
. text/x-python

. application/sql
. text/css
. text/html
. text/javascript
. text/x-java-source

"""


def get_implementation(stream:StringIO, type:str, name:str|None) -> str:
    """Returns the contents of a curly-brace delimited implementation"""
    
    if type == 'objectscript':
        return get_impl_cos(stream)
    if type in ('text/plain',):
        return get_impl_text(stream)
    elif type == 'application/json':
        return get_impl_json(stream)
    elif type in ('application/xml', 'text/xml'):
        return get_impl_xml(stream, name)
    elif type in ('python', 'application/python', 'text/x-python'):
        return get_impl_python(stream, name)
    
    raise ValueError(f"Don't know how to parse '{type}' implementations")


def get_impl_cos(stream:StringIO) ->str:
    """Returns an ObjectScript method implementation"""
    
    lines = []
    state = State()
    while True:
        line = get_line(stream)
        if line.strip() == '}' and state.empty():
            break
        get_impl_cos_state(line, state)
        lines.append(line)
    
    return '\n'.join(lines)


def get_impl_cos_state(line:str, state:'State'):
    """Maintains method parsing state
    
    The return value indicates whether a single brace in line should be
    considered part of the implementation or not (in the latter case it
    is the implementation-closing brace).
    """
    
    i = 0
    while i < len(line):
        c = line[i]
        i += 1
        
        if state.state == '':
            if c == ';':
                # Comment to end of line
                return False
            if line[i-1:i+1] == '//':
                # Comment to end of line
                return False
            if c == '"':
                # Quoted string
                state.push('inq')
            elif line[i-1:i+1] == '/*':
                # Multiline comment
                i += 1
                state.push('inmlc')
            elif line[i-1:].startswith('&html<'):
                # Embedded html
                i += 5
                state.push('html', 1)
            elif c == '{':
                state.depth += 1
            elif c == '}':
                state.depth -= 1
        
        elif state.state == 'inq':
            # In a quoted string
            if c == '"':
                if i < len(line) and line[i] == '"':
                    i += 1
                else:
                    state.pop()
        
        elif state.state == 'inmlc':
            # In a multiline comment
            if line[i-1:i+1] == '*/':
                i += 1
                state.pop()
        
        elif state.state == 'html':
            if c == '<':
                state.depth += 1
            # Hack: embedded javascript can contain =>, so check for that.
            # But now this contrived case fails: &html<=>...
            elif c == '>' and not (i > 1 and line[i-2] == '='):
                state.depth -= 1
                if not state.depth:
                    state.pop()
        
    return


def get_impl_xml(stream:StringIO, name:str|None) -> str:
    """Returns the implementation of a [text|application]/xml xdata"""
    
    lines = []
    root = ''
    done = False
    while True:
        line = get_line(stream)
        if done:
            if line.strip() != '}':
                raise ValueError(f"Parse error looking for closing brace in xdata {name or '(unknown)'}")
            break
        
        if root == '':
            if line == '}':
                # Empty XData block
                break
            data = line.lstrip()
            if (m := re.match(r'<\?.+\?>', data)):
                # XML declaration or other processing instruction
                data = data[m.end(0):].lstrip()
            if (m := re.match(r'<([^\s>\'"]+)\b', data)):
                # First found XML element
                root = m[1]
        
        if root != '':
            if line.endswith(f"</{root}>"):
                # Found closing XML element; still need to find the
                # closing xdata brace
                done = True
        
        lines.append(line)
    
    return '\n'.join(lines)


def get_impl_text(stream:StringIO) -> str:
    """Returns the implementation of a text/plain xdata"""
    
    lines = []
    while True:
        # Single closing brace ends the XData; it can't be part of the
        # contents.
        line = get_line(stream)
        if line == '}':
            break
        lines.append(line)
    
    return '\n'.join(lines)


def get_impl_json(stream:StringIO) -> str:
    """Returns the implementation of a application/json xdata"""
    
    lines = []
    state = State()
    while True:
        line = get_line(stream)
        if line.strip() == '}' and state.depth == 0:
            break
        get_impl_json_state(line, state)
        lines.append(line)
    
    return '\n'.join(lines)


def get_impl_json_state(line:str, state:'State'):
    """Maintains json xdata parsing state"""
    
    i = 0
    while i < len(line):
        c = line[i]
        i += 1
        if state.state == '':
            if c == '{':
                state.depth += 1
            elif c == '}':
                if not state.depth:
                    return '', 0
                state.depth -= 1
            elif c == '"':
                state.push('inq')
        elif state.state == 'inq':
            if c == '"':
                if i < len(line) and line[i] == '"':
                    i += 1
                else:
                    state.pop()
            
    return


def get_impl_python(stream:StringIO, name:str|None) -> str:
    """Returns the implementation of a python method or xdata"""
    
    lines = []
    state = State()
    while True:
        line = get_line(stream)
        get_impl_python_state(line, state)
        if line == '}' and state.empty():
            break
        lines.append(line)
    
    return '\n'.join(lines)


def get_impl_python_state(line:str, state:'State'):
    """Maintains Python method parsing state"""
    
    i = -1
    while i < len(line):
        i += 1
        
        if state.empty():
            if line[i:i+3] == '"""':
                state.state = 'tqd'
                i += 2
            elif line[i:i+3] == "'''":
                state.state = 'tqs'
                i += 2
        
        elif state.state == 'tqd':
            if line[i:i+3] == '"""':
                state.state = ''
                i += 2
        
        elif state.state == 'tqs':
            if line[i:i+3] == "'''":
                state.state = ''
                i += 2



# ===== =====


class State():
    """Simple parsing state stack"""
    
    # Used in push() and pop()
    _states:list[tuple[str,int]]
    
    state:str
    depth:int
    
    def __init__(self) -> None:
        self._states = []
        self.state = ''
        self.depth = 0
    
    def empty(self) -> bool:
        return not self.state and self.depth == 0
    
    def push(self, state:str, depth:int = 0) -> None:
        self._states.append((self.state, self.depth))
        self.state = state
        self.depth = depth
    
    def pop(self) -> bool:
        self.state, self.depth = self._states.pop()
        return self.empty()
    
    def __str__(self) -> str:
        return f"State('{self.state}',{self.depth})"
    def __repr__(self) -> str:
        return f"State('{self.state}',{self.depth})"


