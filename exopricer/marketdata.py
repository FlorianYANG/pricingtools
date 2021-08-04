class Underlying:
    def __init__(self, name):
        self.name = name


class Share(Underlying):
    def __init__(self, name, spot=None, vol=None, div=None, cor=None):
        super(Share, self).__init__(name)
        self.type = "Share"
        self.spot = spot
        self.vol = vol
        self.div = div
        if cor:
            pass
        else:
            self.cor = {}

    def __copy__(self):
        new = Share(self.name, self.spot, self.vol, self.div, self.cor)
        return new



class MarketData:
    def __init__(self):
        self.underlying = {}
        self.r = None

    def simple_update(self, undl, **kwargs):
        if "type" in kwargs:
            if kwargs["type"] == "Share":
                self.underlying[undl] = Share(undl)
        else:
            raise ValueError("Should have at least type")
        if "spot" in kwargs:
            self.underlying[undl].spot = kwargs["spot"]
        if "vol" in kwargs:
            self.underlying[undl].vol = kwargs["vol"]
        if "div" in kwargs:
            self.underlying[undl].div = kwargs["div"]
        if "cor" in kwargs:
            for k, v in kwargs["cor"].items():
                self.underlying[undl].cor[k] = v
                # self.underlying[k].cor[undl] = v

    def __copy__(self):
        new_marketdata = MarketData()
        new_marketdata.r = self.r
        for underlying in self.underlying.keys():
            new_marketdata.underlying[underlying] = self.underlying[underlying].__copy__()
        return new_marketdata