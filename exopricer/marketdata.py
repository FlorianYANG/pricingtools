class MarketData:
    def __init__(self):
        self.spot = {}
        self.vol = {}
        self.div = {}
        self.type = {}
        self.r = None

    def simple_update(self, undl, **kwargs):
        if "type" in kwargs:
            self.type[undl] = kwargs["type"]
        if "spot" in kwargs:
            self.spot[undl] = kwargs["spot"]
        if "vol" in kwargs:
            self.vol[undl] = kwargs["vol"]
        if "div" in kwargs:
            self.div[undl] = kwargs["div"]
