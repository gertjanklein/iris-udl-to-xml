from udl2xml.main import determine_type

UDL_CLS = """
/* Copyright */

Include %occInclude

/// Class doc
Class Test.Test2
{

}
"""

UDL_RTN = """
ROUTINE Name [Type=INC]
#include %occErrors
"""


def test_type_cls():
    type, name = determine_type(UDL_CLS)
    assert type == 'cls', "Class correctly recognized"
    assert name == 'Test.Test2', "Class name correctly extracted"


def test_type_rtn():
    type, name = determine_type(UDL_RTN)
    assert type == 'inc', "Routine type correctly recognized"
    assert name == 'Name', "Routine name correctly extracted"

