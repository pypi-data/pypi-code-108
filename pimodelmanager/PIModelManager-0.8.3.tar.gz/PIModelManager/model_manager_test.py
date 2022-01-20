from PIModelManager import ModelManager


def test_manager_singleton():
    m1 = ModelManager()
    
    m1._credentials = {"test_credential" : 123}
    assert m1._credentials == {"test_credential" : 123}
    assert ModelManager()._credentials == {"test_credential" : 123}
    
    m2 = ModelManager()
    assert id(m1) == id(m2)
    assert m2._credentials == {"test_credential" : 123}
    assert ModelManager()._credentials == {"test_credential" : 123}
    
    m2._credentials = {"test_credential" : 456}
    assert m1._credentials == {"test_credential" : 456}
    assert m2._credentials == {"test_credential" : 456}
    assert ModelManager()._credentials == {"test_credential" : 456}
