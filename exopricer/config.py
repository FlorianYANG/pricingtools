import numpy as np


class Engine:
    def __init__(self):
        self.type = None  # Const, T, ST
        self.model = None


class Vol(Engine):
    def __init__(self, typename):
        super(Vol, self).__init__()
        self.type = typename
        self.model = {}

    def construct(self, md, undls):
        if self.type == "Const":
            for undl in undls:
                self.model[undl] = lambda M, T: md.underlying[undl].vol

    def calculate(self, undl, M, T):
        return self.model[undl](M, T)


class Discount(Engine):
    def __init__(self, typename):
        super(Discount, self).__init__()
        self.type = typename

    def construct(self, md):
        if self.type == "Const":
            self.model = lambda M, T: np.exp(md.r, T)

    def calculate(self, M, T):
        return self.model(M, T)


class Forward(Engine):
    def __init__(self, typename):
        super(Forward, self).__init__()


class Forex(Engine):
    def __init__(self, typename):
        super(Forex, self).__init__()


class Config:
    def __init__(self, v="Const", d="Const", fwd="Const", fx="Const"):
        self.vol = Vol("Const")
        self.discount = Discount("Const")
        self.forward = Forward("Const")
        self.forex = Forex("Const")
        self.with_delta = False
        self.with_gamma = False
        self.with_vega = False
        self.with_theta = False

        self.dt = 1/256
        self.path = 10000
        self.engine = "MonteCarlo"
        self.antithetic = True # much more efficient than I originally thought

    def with_greeks(self, items=None, all=False):
        if all:
            self.with_delta = True
            self.with_gamma = True
            self.with_vega = True
            self.with_theta = True
            return
        if isinstance(items, str):
            items = [items]
        for item in items:
            if item == "delta":
                self.with_delta = True
            if item == "gamma":
                self.with_gamma = True
            if item == "vega":
                self.with_vega = True
            if item == "theta":
                self.with_theta = True

