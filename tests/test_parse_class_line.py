from udl2xml.cvt_class import parse_class_line


def test_bare():
    line = "Class a.b {"
    
    super, kwds = parse_class_line(None, line)
    
    assert super is None, "Bare class line adds no superclass"
    assert not kwds, "Bare class line has no class keywords"


def test_super_single():
    line = "Class Test.Test3 Extends %Persistent {"
    
    super, kwds = parse_class_line(None, line)
    
    assert super == "%Persistent", "Superclass extracted"
    assert not kwds, "No class keywords"


def test_class_kwds():
    line = "Class Test.Test3 [ Abstract, CompileAfter = e.f, DependsOn = (a.b, c.d) ] {"
    
    super, kwds = parse_class_line(None, line)
    
    assert super is None, "No superclass"
    assert kwds == [('Abstract', '1'), ('CompileAfter', 'e.f'), ('DependsOn', 'a.b,c.d')], "Class keywords found"


def test_super_and_keywords():
    line = "Class Test.Test3 Extends %Persistent [ Abstract ] {"
    
    super, kwds = parse_class_line(None, line)
    
    assert super == "%Persistent", "Superclass extracted"
    assert kwds == [('Abstract', '1')], "Class keyword found"

