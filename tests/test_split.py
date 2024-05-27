from udl2xml.split import split_nv


def test_basic():
    """Test simple n=v list"""
    
    udl = "[ a = b, c = d ]"
    res = list(split_nv(udl))
    
    assert len(res) == 2, "Two items found"
    assert res[0] == ('a', 'b'), "First parameter found"
    assert res[1] == ('c', 'd'), "First parameter found"


def test_space_before_comma():
    """Test space before separator handled properly"""
    
    udl = "[ a = b , c = d ]"
    res = list(split_nv(udl))
    
    assert len(res) == 2, "Two items found"
    assert res[0] == ('a', 'b'), "First parameter found"
    assert res[1] == ('c', 'd'), "First parameter found"


def test_negative_value():
    """Tests that negative values are properly parsed"""
    
    udl = "(MAXLEN = -1)"
    res = list(split_nv(udl))
    
    assert len(res) == 1, "Item found"
    assert res[0] == ('MAXLEN', '-1'), "First parameter found"

