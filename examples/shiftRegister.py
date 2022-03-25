class shiftRegister:
    def __init__(self) -> None:
        self.value = 0
        self.index = 0
        pass

    def addNew(self, car):
        if car > 0 and car <10:
            self.value += car*10**self.index
            self.index +=1
        elif car<=0:
            raise ValueError("input too small")
        elif car >10:
            raise ValueError("input too big")
        pass

    def remove(self):
        if self.index > 0:
            self.value= int(self.value//10)
            self.index -=1
        else: raise RuntimeError

    def read(self):
        return int(self.value-(int((self.value//10))*10))
    
    def out(self):
        return self.value, self.index
    pass

    def clear(self):
        self.value = 0
        self.index = 0