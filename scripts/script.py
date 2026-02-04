class TestBase:
    pass

class TestChildA(TestBase):
    pass

class TestChildB(TestBase):
    pass


print(TestBase.__subclasses__())