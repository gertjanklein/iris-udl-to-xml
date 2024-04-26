import sys, io
import re
import argparse

from cvt_routine import convert_rtn
from cvt_class import convert_cls


def main():
    parser = argparse.ArgumentParser(description='Convert UDL to XML.')
    
    parser.add_argument('--in', dest='input_file', metavar='FILE', help='Input file name. If not provided, input is read from stdin.')
    parser.add_argument('--out', dest='output_file', metavar='FILE', help='Output file name. If not provided, output is written to stdout.')
    args = parser.parse_args()
    
    if not sys.stdin.isatty():
        # Make sure stdin expects UTF-8
        sys.stdin = io.TextIOWrapper(sys.stdin.detach(), encoding='utf-8')
        udl = sys.stdin.read()
    elif args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            udl = f.read()
    else:
        # No input; display help and exit
        parser.print_help()
        sys.exit(1)
    
    xml = convert(udl)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(xml)
    else:
        # Make sure stdout writes UTF-8
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
        sys.stdout.write(xml)


def convert(udl:str) -> str:
    """Converts class or routine in UDL syntax to XML"""
    
    # Determine what type of source we have, and the name of the item in it.
    type, name = determine_type(udl)
    
    if type == 'cls':
        return convert_cls(udl, name)
    
    return convert_rtn(udl, name, type)


def determine_type(udl:str):
    """Returns a (type, name) tuple for the UDL contents"""
    
    # Remove leading whitespace for match below
    udl = udl.lstrip()
    
    if m := re.match(r'ROUTINE (\S+) \[Type=(\S+)\]', udl):
        return m[2].lower(), m[1]
    if m := re.search(r'(?m)^Class (\S+)\b', udl):
        return 'cls', m[1]
    
    raise ValueError("Data does not appear to be UDL.")



if __name__ == '__main__':
    main()

