from split import split_nv


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


