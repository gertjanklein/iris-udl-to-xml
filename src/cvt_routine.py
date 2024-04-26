import re

from lxml import etree
from lxml.etree import CDATA


def convert_rtn(udl:str, name:str, type:str) -> str:
    """Converts a routine UDL to XML export format."""

    spec, impl = udl.split('\n', maxsplit=1)
    if not (m := re.match(r'ROUTINE\s+([\w.%]+)\s+\[Type\s*=\s*([^\]]+)]', spec)):
        raise ValueError(f"Parse error: don't know how to parse {spec}")
    name = m[1]
    type = m[2]

    root = etree.Element("Export", attrib=dict(generator="IRIS", version="26"))
    root.text = '\n'
    root.tail = '\n'
    rtn = etree.SubElement(root, "Routine", name=name, type=type)
    rtn.tail = '\n'
    rtn.text = CDATA('\n'+impl)

    # Convert XML tree to string
    bytes = etree.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=False, with_tail=True)
    result = bytes.decode()

    return result

