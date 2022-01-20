from nwutils.list import flattenList

class TestFlattenList:
    def test_flattenList_1(self):
        a = []
        assert flattenList(a) == []

    def test_flattenList_2(self):
        a = [1,2,3,4,5]
        assert flattenList(a) == [1,2,3,4,5]
    
    def test_flattenList_3(self):
        a = [1, [2,3], [4,[5,[6]]]]
        assert flattenList(a) == [1,2,3,4,5, 6]

    def test_flattenList_4(self):
        a = [{1, 2}, [{"1":2, "2":{"2_1":2, "2_2":3}}, (1,2,3)], ["hi", "there"], "hi", None]
        assert flattenList(a) == [{1,2}, {"1":2, "2":{"2_1":2, "2_2":3}}, (1,2,3), "hi", "there", "hi", None]
    
    def test_flattenList_5(self):
        a = {"a":[1,2,3], "b":[5, 6, (7, )]}
        assert flattenList(a.values()) == [1,2,3,5,6,(7,)]