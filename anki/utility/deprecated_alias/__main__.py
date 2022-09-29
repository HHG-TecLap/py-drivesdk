from alias import deprecated_alias, alias, AliasMeta

class Class(metaclass=AliasMeta):
    @deprecated_alias("deprecated_test")
    @alias("undeprecated_test")
    def test(self):
        print("Test!")

def main():
    obj = Class()

    obj.test()
    obj.undeprecated_test()
    obj.deprecated_test()
    obj.deprecated_test()
    pass

if __name__=="__main__": main()