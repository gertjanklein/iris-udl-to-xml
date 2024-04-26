import re
from io import StringIO

from lxml import etree
from lxml.etree import CDATA

from util import add_el, extract, read_until, unquote
from split import split_nv
from implementation import get_implementation


def handle_xdata(cls:etree._Element, stream:StringIO, line:str, doc:str|None):
    """Handles an XData declaration in a class definition"""
    
    # Read up to the terminating character and remove it
    line = read_until(stream, line, '{')
    
    # First determine the xdata name
    if not (m := re.match(r'XData ([\w%]+)\b', line, re.I)):
        raise ValueError("Can't determine xdata name")
    name = m[1]
    line = line[m.end(0):].lstrip()
    
    xdata = add_el(cls, 'XData', '\n', 2, attr={'name':name})
    if doc:
        add_el(xdata, 'Description', f"\n{doc}")
    
    # Default mime type if not specified/overridden.
    mime = 'text/xml'
    
    # Keywords, if any
    if line and line[0] == "[":
        kwds = extract(line)
        for n, v in split_nv(kwds):
            if v and v[0] == '"':
                v = unquote(v)
            add_el(xdata, n, v)
            # Remember actual mimetype, if different from default
            if n == 'MimeType':
                mime = v
        line = line[len(kwds):].lstrip()
    
    # Sort for compatibility with IRIS export
    xdata[:] = sorted(xdata, key=lambda el: ORDER.get(el.tag, 999))
    
    impl = get_implementation(stream, mime, name)
    if impl:
        if '\n' in impl:
            impl = '\n' + impl
        impl = impl + '\n'
        # if not ']]>' in impl:
        #     impl = CDATA(impl)
        add_el(xdata, 'Data', impl)


# Order in which subelements appear in an xml export. Based
# on order in oddDEF.
ORDER = {
    "Origin": 2,
    "Description": 4,
    "Sequencenumber": 11,
    "Keyworderror": 12,
    "Keywordmodified": 13,
    "Internal": 14,
    "Deprecated": 17,
    "Data": 21,
    "Schemaspec": 22,
    "Xmlnamespace": 23,
    "Mimetype": 24,
}

