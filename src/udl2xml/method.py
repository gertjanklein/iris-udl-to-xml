import re
from io import StringIO

from lxml import etree
from udl2xml.util import CDATA

from udl2xml.util import add_el, extract, get_quoted_string, get_word, unquote, read_until
from udl2xml.split import split_nv
from udl2xml.implementation import get_implementation


def handle_method(cls:etree._Element, stream:StringIO, line:str, doc:str|None, lang:str='objectscript'):
    """Handles a method declaration in a class definition"""
    
    # Method may be formatted with "Multiline method arguments",
    # so make sure we have everyting we need
    line = read_until(stream, line, '{')
    
    # First determine the method name and type. Name may be quoted.
    if not (m := re.match(r'(?:Class)?Method ((?:[\w%]+)|(?:"[^"]+"))\s*\(', line)):
        raise ValueError(f"Parse error around {line}")
    name = m.group(1)
    if name[0] == '"':
        name = unquote(name)
    classmethod = line.startswith('Class')
    line = line[m.end(1):]
    
    # Create element for the method
    method = add_el(cls, 'Method', '\n', 2, {'name':name})
    if classmethod:
        add_el(method, 'ClassMethod', "1")
    if doc:
        add_el(method, 'Description', f"\n{doc}")
    
    # Method parameters, convert to formal spec
    parms = extract(line)
    line = line[len(parms):].lstrip()
    spec = parse_parameters(parms)
    if spec != '':
        add_el(method, 'FormalSpec', spec)
    
    # Method return type, if any
    if (m := re.match(r'As ([\w%.]+)\b', line, re.I)):
        type = m[1]
        add_el(method, 'ReturnType', type)
        line = line[m.end():].lstrip()
        
        # Method return type parameters, if any
        if line and line[0] == '(':
            spec = extract(line)
            fspec = condense_type_parameters(spec)[1:-1]
            add_el(method, 'ReturnTypeParams', fspec)
            line = line[len(spec):].lstrip()
    
    # Method keywords, if any
    if line and line[0] == "[":
        kwds = extract(line)
        for n, v in split_nv(kwds):
            if n == 'Language':
                lang = v
            # More keywords can have multiple values?
            elif n in 'PublicList'.split():
                if v[0] == '(':
                    v = v[1:-1].replace(', ', ',')
            elif v and v[0] == '"':
                v = unquote(v)
            add_el(method, n, v)
        line = line[len(kwds):].lstrip()
    
    if line:
        raise ValueError(f"Parse error in method {name} around:'{line}'")
    
    # Sort for compatibility with IRIS export
    method[:] = sorted(method, key=lambda el: ORDER.get(el.tag, 999))
    
    # Get method implementation
    impl = get_implementation(stream, lang, name)
    if impl:
        if '\n' in impl:
            impl = '\n' + impl + '\n'
        else:
            # Single line: no leading newline
            impl = impl + '\n'
        add_el(method, 'Implementation', CDATA(impl))


def parse_parameters(parms:str) -> str:
    """Converts function parameter list into a formal spec"""
    
    # Function parameter still surrounded by parenthesis, strip those
    data = parms[1:-1].strip()
    if data == '':
        return ''
    
    lst = []
    while data != '':
        # In this regex:
        # - Output or ByRef (optional)
        # - name (optionally followed by 3 dots)
        # - As Something (optional)
        if not (m := re.match(r'(?:(Output|ByRef)\s+)?([\w%]+(?:\.\.\.)?)(?:\s+As\s+([\w%.]+))?', data, re.I)):
            raise ValueError(f"Error parsing method parameter list around {data}")
        data = data[m.end(0):].lstrip()
        
        # Get name
        pspec = m[2]
        if m[1]:
            # Prefix with Output or ByRef
            pspec = {'output':'*', 'byref':'&'}[m[1].lower()] + pspec
        if m[3]:
            # Add Type
            pspec = pspec + ':' + m[3]
        
        if data and data[0] == '(':
            # Parameter type parameters; split to re-assemble without spaces
            ptp = extract(data)
            pspec += condense_type_parameters(ptp)
            data = data[len(ptp):].lstrip()
            
        if data and data[0] == '=':
            # Default value
            data = data[1:].lstrip()
            if data[0] == '"':
                default = get_quoted_string(data)
                pspec += f"={default}"
                data = data[len(default):].lstrip()
            elif data[0] == '{':
                default = extract(data)
                data = data[len(default):].lstrip()
                if default[0] == '{':
                    if not any(c in default[1:-1] for c in ',{}'):
                        default = default[1:-1]
                pspec += f"={default}"
            else:
                default = get_word(data)
                pspec += f"={default}"
                data = data[len(default):].lstrip()
        
        lst.append(pspec)
        
        if data:
            if data[0] == ',':
                data = data[1:].lstrip()
            else:
                raise ValueError(f"Parse error around {data}")
    
    return ','.join(lst)


def condense_type_parameters(type_parms:str) -> str:
    """Condenses type parameters ("MAXLEN = 1" -> "MAXLEN=1")"""
    
    ptp_list = []
    for n, v in split_nv(type_parms):
        ptp_list.append(f'{n}={v}')
    return f"({','.join(ptp_list)})"


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Description": 4,
    "Final": 7,
    "NotInheritable": 9,
    "Internal": 14,
    "Deprecated": 17,
    "Abstract": 21,
    "ClassMethod": 23,
    "ClientName": 24,
    "CodeMode": 25,
    "FormalSpec": 27,
    "GenerateAfter": 29,
    "Language": 32,
    "NoContext": 33,
    "PlaceAfter": 38,
    "Private": 39,
    "ProcedureBlock": 40,
    "PublicList": 41,
    "ReturnType": 42,
    "SqlName": 45,
    "SqlProc": 46,
    "WebMethod": 51,
    "ZenMethod": 52,
    "SoapBindingStyle": 53,
    "SoapBodyUse": 54,
    "ServerOnly": 59,
    "SoapNameSpace": 61,
    "ReturnTypeParams": 62,
    "ExternalProcName": 63,
    "ReturnResultsets": 64,
    "SoapTypeNameSpace": 65,
    "SoapAction": 67,
    "SoapMessageName": 68,
    "ClientMethod": 70,
    "ForceGenerate": 71,
    "SoapRequestMessage": 73,
    "SqlRoutine": 74,
    "Requires": 75,
}