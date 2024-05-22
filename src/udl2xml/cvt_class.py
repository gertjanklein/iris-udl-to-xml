import re
from io import StringIO

from lxml import etree

from udl2xml.split import split_nv
from udl2xml.util import add_comment, add_el, get_line, startswithi, extract, get_word, unquote

from udl2xml.foreignkey import handle_foreignkey
from udl2xml.index import handle_index
from udl2xml.method import handle_method
from udl2xml.parameter import handle_parameter
from udl2xml.projection import handle_projection
from udl2xml.property import handle_property
from udl2xml.query import handle_query
from udl2xml.storage import handle_storage
from udl2xml.trigger import handle_trigger
from udl2xml.xdata import handle_xdata


def convert_cls(udl:str, name:str) -> str:
    """Converts a class in UDL syntaxt to XML"""

    # Create Export and Class XML elements
    root, cls = create_class(name)

    stream = StringIO(udl)

    # Default implementation language
    lang = 'objectscript'

    # Parse outer class syntax
    state = ''
    for line in stream:
        if line[-1] == '\n':
            line = line[:-1]
        if line == '':
            continue

        if state == '':
            if line.startswith('/*'):
                # Outside the class, a comment is considered to mean Copyright
                value = collect_comment(stream, line)
                el = add_el(cls, "Copyright", value)

            elif startswithi(line, 'Import'):
                el = add_el(cls, 'Import')
                el.text = strip_parens(line[6:])

            elif startswithi(line, 'Include'):
                # Include, IncludeGenerator
                name = line.split()[0]
                text = strip_parens(line[len(name):])
                if name == 'Include':
                    name = 'IncludeCode'
                el = add_el(cls, name, text)

            elif line.startswith('///'):
                doc = collect_doc(stream, line)
                el = add_el(cls, "Description", '\n'+doc)

            elif startswithi(line, 'Class'):
                # Determine superclass(es) and class keywords
                super, kwds = parse_class_line(stream, line)
                if super:
                    el = add_el(cls, 'Super', super)
                for name, value in kwds:
                    if name == 'Language':
                        lang = value
                    el = add_el(cls, name, value)
                state = 'class'

                # Sort for compatibility with IRIS export
                cls[:] = sorted(cls, key=lambda el: ORDER.get(el.tag, 999))
                # Whitespace adjustment for compatibility
                if len(cls) and cls[-1].tag in 'DependsOn NoExtent QueryClass Inheritance GeneratedBy'.split():
                    cls[-1].tail += '\n'


            else:
                raise ValueError(f"Parse error on line {line}")

        elif state == 'class':
            doc = None

            # "// something": single line comment
            if re.match(r'//$|// (.*)?$', line):
                add_comment(cls, '\n'+line+'\n\n')
                continue

            # "/* ...": start of multiline comment
            if line.startswith('/*'):
                value = collect_comment(stream, line)
                add_comment(cls, '\n'+value+'\n')
                continue

            # Documentation for something to follow
            if line.startswith('///'):
                doc = collect_doc(stream, line)
                line = get_line(stream)

            # Members

            if startswithi(line, ('Property ', 'Relationship')):
                handle_property(cls, stream, line, doc)

            elif startswithi(line, ('ClassMethod ', 'Method')):
                handle_method(cls, stream, line, doc, lang)

            elif startswithi(line, 'Parameter'):
                handle_parameter(cls, stream, line, doc)

            elif startswithi(line, 'XData'):
                handle_xdata(cls, stream, line, doc)

            elif startswithi(line, 'Index'):
                handle_index(cls, stream, line, doc)

            elif startswithi(line, 'Storage'):
                handle_storage(cls, stream, line, doc)

            elif startswithi(line, 'Query'):
                handle_query(cls, stream, line, doc)

            elif startswithi(line, 'ForeignKey'):
                handle_foreignkey(cls, stream, line, doc)

            elif startswithi(line, 'Projection'):
                handle_projection(cls, stream, line, doc)

            elif startswithi(line, 'Trigger'):
                handle_trigger(cls, stream, line, doc, lang)

            else:
                if not line.strip() == '}':
                    raise ValueError(f"Parse error: don't know how to handle {line}")
                else:
                    state = 'done'

        elif state == 'done':
            if line:
                raise ValueError(f"Parse error: unexpected data after class def: {line}")

    # Remove extra newline from last item, to mimick what IRIS does
    root[0][-1].tail = '\n'

    # Convert XML tree to string
    bytes = etree.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=False, with_tail=True)
    result = bytes.decode()

    return result


def parse_class_line(stream:StringIO, line:str):
    """Parses a Class Xxx line
    
    Returns (super, [kwlist])
    
    """
    
    while not line[-1] == '{':
        line += '\n' + get_line(stream)
    line = line[:-1].rstrip()
    
    m = re.match(r'Class\s+\S+(\s+Extends\s+)?', line, re.S|re.I)
    if not m:
        raise ValueError(f"Parse error around: '{line}'")
    line = line[m.end():].lstrip()
    
    if m[1]:
        # Extends must be followed by class name or list
        if line[0] == '(':
            super = extract(line)
            line = line[len(super):].lstrip()
            super = super[1:-1].replace(', ', ',')
        else:
            super = get_word(line, '.')
            line = line[len(super):].lstrip()
    else:
        super = None
    
    kwds = []
    if line and line[0] == '[':
        kwline = extract(line)
        line = line[len(kwline):].lstrip()
        for n, v in split_nv(kwline):
            if v and v[0] == '{':
                v = v[1:-1]
            elif v and v[0] == '(':
                v = v[1:-1]
                v = v.replace(', ', ',')
            elif v and v[0] == '"':
                v = unquote(v)
            kwds.append((n, v))
    
    if line:
        raise ValueError(f"Parse error in class declaration around: '{line}'")
    
    return super, kwds


def collect_doc(stream:StringIO, line:str) -> str:
    """Returns all lines starting with /// concatenated"""
    
    lines = []
    while True:
        if line == '///':
            lines.append('')
        elif line[3] != ' ':
            lines.append(line[3:])
        else:
            lines.append(line[4:])
        
        # Remember current position in stream
        here = stream.tell()
        
        # Get next line
        line = get_line(stream)
        
        # If it is part of the documentation, go handle it
        if line.startswith('///'):
            continue
        
        # Rewind to were we where, and quit the loop
        stream.seek(here)
        break
    
    return '\n'.join(lines)


def collect_comment(stream:StringIO, line:str) -> str:
    lines = []
    
    while True:
        # Add line to list
        lines.append(line)
        
        # If this is the last line of the comment, we're done
        if line.endswith('*/'):
            break
        
        # Get next line and strip newline
        line = get_line(stream)
    
    return '\n'.join(lines)


def strip_parens(text:str):
    """Returns text with surrounding parens removed, if present"""
    
    text = text.strip()
    if not (text[0] == '(' and text[-1] == ')'):
        return text
    
    # Remove parenthesis
    text = text[1:-1]
    
    # Remove whitespace around items in comma-separated list
    parts = [ part.strip() for part in text.split(',') ]
    return ','.join(parts)


def create_class(name):
    """Creates an export element containing a class export"""
    
    root = etree.Element("Export", attrib=dict(generator="IRIS", version="26"))
    root.text = '\n'
    root.tail = '\n'
    cls = etree.SubElement(root, "Class", name=name)
    cls.text = '\n'
    cls.tail = '\n'
    return root, cls


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Description": 4,
    "Final": 7,
    "Deprecated": 17,
    "Abstract": 21,
    "ClassType": 23,
    "ClientDataType": 24,
    "CompileAfter": 28,
    "DdlAllowed": 29,
    "Hidden": 32,
    "Import": 33,
    "IncludeCode": 35,
    "IncludeGenerator": 37,
    "Language": 39,
    "NoContext": 42,
    "OdbcType": 43,
    "Owner": 44,
    "ProcedureBlock": 46,
    "PropertyClass": 48,
    "SqlCategory": 52,
    "SqlRowIdName": 55,
    "SqlRowIdPrivate": 56,
    "SqlTableName": 58,
    "StorageStrategy": 59,
    "Super": 60,
    "System": 61,
    "ViewQuery": 65,
    "SoapBindingStyle": 70,
    "SoapBodyUse": 71,
    "ClientName": 73,
    "NoExtent": 76,
    "QueryClass": 79,
    "ConstraintClass": 80,
    "IndexClass": 81,
    "ProjectionClass": 82,
    "MemberSuper": 83,
    "DependsOn": 84,
    "GeneratedBy": 87,
    "ServerOnly": 88,
    "Inheritance": 92,
    "LegacyInstanceContext": 96,
    "TriggerClass": 99,
    "EmbeddedClass": 100,
    "Sharded": 104,
    "Copyright": -1, # is 105 but copyright comes first if present
}
