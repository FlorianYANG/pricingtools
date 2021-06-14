from collections import defaultdict
from copy import copy
from . import engine
from .config import Config

class Product:
    def __init__(self):
        self.payoff = Payoff()
        self.params = Params() # dict like
        self.marketdata = None # class
        self.config = Config()
        self.result = None
        self.undls = None # to be diffused

    def build(self, undls=None):
        if isinstance(undls, str):
            undls = [undls]

        # build model
        self.undls = undls
        self.config.vol.construct(self.marketdata, undls)
        self.config.discount.construct(self.marketdata)
        self.payoff.construct()
        # self.config.forward

    def price(self):
        if self.config.engine == "MonteCarlo":
            return engine.MonteCarlo(self)
        raise NotImplementedError

class Params():
    def __init__(self):
        self.data = dict()

    def __setitem__(self, k, v):
        self.data[k] = v

    def __getitem__(self, var, d=None):
        assert var in self.data
        if d != None:
            if isinstance(self.data[var], list):
                return self.data[var][d]
            else:
                raise
        else:
            return self.data[var]

    def __copy__(self):
        _params = Params()
        for k, v in self.data.items():
            try:
                _params.data[k] = copy(v)
            except:
                _params.data[k] = v
        return _params

    def add(self, data):
        for k, v in data.items():
            self.data[k] = v

    def copy(self):
        return self.__copy__()

    def get(self, var, d=None):
        return self.__getitem__(var, d)

    def update(self, var, val, d=None):
        if d:
            self.data[var][d] = val
        else:
            self.data[var] = val


class Payoff(defaultdict):
    def __init__(self):
        super(Payoff, self).__init__(list)
        self.dates = []
        self.duplicate = defaultdict(int)
        self.rt_duplicate = None

    def add(self, id, func):
        self.duplicate[func.__name__] += 1

        if isinstance(id, int):
            self[id].append(func)
        elif isinstance(id, list):
            for i in id:
                assert isinstance(i, int)
                self[i].append(func)
        else:
            raise ValueError

    def construct(self):
        for i in self.keys():
            if not isinstance(i, int):
                raise ValueError("register number as key in payoff {i}")
            self.dates.append(i)
        self.dates.sort()

    def getact(self):
        pass