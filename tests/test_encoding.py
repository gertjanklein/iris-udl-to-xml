from udl2xml.main import convert


def test_outside_bmp():
    """Test characters outside BMP survive conversion"""
    
    udl = """
/// 🗐
Class x
{

}
""".lstrip()
    result = convert(udl)
    assert '🗐' in result, "Character outside BMP survives conversion"
