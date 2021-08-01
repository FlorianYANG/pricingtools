from collections import defaultdict
from . import engine
from .config import Config


class Product:
    def __init__(self):
        self.payoff = Payoff()
        self.params = Params() # dict like
        self.marketdata = None # class
        self.config = Config()
        self.result = None
        self.underlyings = None # to be diffused


    def price(self):
        # assure underlying
        if isinstance(self.underlyings, str):
            self.underlyings = [self.underlyings]

        result = {}
        original_marketdate = self.marketdata.__copy__()
        if self.config.engine == "MonteCarlo":
            price_base = engine.MonteCarlo(self)
            result["price"] = price_base
            print("base: ", price_base)

            if self.config.with_theta:
                shift_payoff = self.payoff.shift(n=-1)
                price_t = engine.MonteCarlo(self, payoff=shift_payoff)
                result["theta"] = price_t-price_base
                print("theta: ", price_t)

            result["delta"] = {}
            result["gamma"] = {}
            result["vega"] = {}

            for underlying in self.underlyings:
                if self.config.with_delta and not self.config.with_gamma:
                    self.marketdata = original_marketdate.__copy__()
                    shift_marketdate.underlying[underlying].spot += 1
                    price_s_up = engine.MonteCarlo(self, marketdata=shift_marketdate)
                    result["delta"][underlying] = price_s_up - price_base
                    print("delta: ", price_s_up)

                elif self.config.with_gamma:
                    shift_marketdate = self.marketdata.__copy__()
                    shift_marketdate.underlying[underlying].spot += 1
                    price_s_up = engine.MonteCarlo(self, marketdata=shift_marketdate)
                    shift_marketdate = self.marketdata.__copy__()
                    shift_marketdate.underlying[underlying].spot -= 1  # TODO: what if current spot is smaller than 1
                    price_s_down = engine.MonteCarlo(self, marketdata=shift_marketdate)
                    result["delta"][underlying] = price_s_up - price_base
                    result["gamma"][underlying] = price_s_up - 2*price_base + price_s_down
                    print("s+1: ", price_s_up, " s-1: ", price_s_down)

                if self.config.with_vega:
                    shift_marketdate = self.marketdata.__copy__()
                    shift_marketdate.underlying[underlying].vol += 0.01
                    price_v_up = engine.MonteCarlo(self, marketdata=shift_marketdate)
                    result["vega"][underlying] = price_v_up - price_base
                    print("v+1: ", price_v_up)

            self.result = result
            return
        raise NotImplementedError


class Params:
    """
    Class to contain all the economics,
    example: Params.K as strike of the option, can also be accessed as Param["K"]
    """
    def __init__(self):
        pass

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __getitem__(self, k):
        return self.__dict__[k]

    def __copy__(self):
        _params = Params()
        _params.__dict__.update(self.__dict__)
        return _params

    def copy(self):
        return self.__copy__()


class Payoff:
    """
    dictionary to store a list of all the payoff event within certain date
    Payoff[day] = [event1, event2]
    """
    def __init__(self):
        self.events = defaultdict(list)
        self.dates = []
        self.occur = defaultdict(int)

    def add(self, id, func):
        """
        add event to Payoff, if id is a list,
        :param id:
        :param func:
        :return:
        """
        if isinstance(id, int):
            self.events[id].append(func)
            self.occur[func.__name__] += 1

        elif isinstance(id, list):
            for i in id:
                assert isinstance(i, int)
                self.events[i].append(func)
            self.occur[func.__name__] += len(id)

        else:
            raise ValueError

    def construct(self):
        for i in self.events.keys():
            if not isinstance(i, int):
                raise ValueError("register number as key in payoff {i}")
            self.dates.append(i)
        self.dates.sort()

    def shift(self, n=-1):
        shift = Payoff()
        for date in self.events.keys():
            if date+n < 1:
                print("currently cant handle passed event")
                for event in self.events[date]:
                    shift.events[0].append(event)
            else:
                for event in self.events[date]:
                    shift.events[date+n].append(event)
        return shift

    def getact(self):
        pass