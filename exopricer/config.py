import numpy as np

class engine:
    def __init__(self):
        self.type = None # Const, T, ST
        self.model = None


class Vol(engine):
    def __init__(self, typename):
        super(Vol, self).__init__()
        self.type = typename
        self.model = {}

    def construct(self, md, undls):
        if self.type == "Const":
            for undl in undls:
                self.model[undl] = lambda M, T: md.vol[undl]

    def calculate(self, undl, M, T):
        return self.model[undl](M, T)


class Discount(engine):
    def __init__(self, typename):
        super(Discount, self).__init__()
        self.type = typename

    def construct(self, md):
        if self.type == "Const":
            self.model = lambda M, T: np.exp(md.r, T)

    def calculate(self, M, T):
        return self.model(M, T)


class Forward(engine):
    def __init__(self, typename):
        super(Forward, self).__init__()


class Forex(engine):
    def __init__(self, typename):
        super(Forex, self).__init__()


class Config():
    def __init__(self, v="Const", d="Const", fwd="Const", fx="Const"):
        self.vol = Vol("Const")
        self.discount = Discount("Const")
        self.forward = Forward("Const")
        self.forex = Forex("Const")

        self.dt = 1/256
        self.path = 10000
        self.engine = None
        self.antithetic = True # much more efficient than I originally thought
