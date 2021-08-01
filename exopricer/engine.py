import numpy as np
import time
from collections import defaultdict


def MonteCarlo(product, payoff=None, marketdata=None):
    time0 = time.time()
    print("start pricing")

    underlyings = product.underlyings
    config = product.config
    params = product.params
    marketdata = marketdata or product.marketdata

    # prepare model
    config.vol.construct(marketdata, underlyings)
    config.discount.construct(marketdata)
    # self.config.forward

    # Prepare dates
    payoff = payoff or product.payoff
    payoff.construct()
    datenumber = max(payoff.dates)
    undlnumber = len(underlyings)

    # random varaible
    rnds = RandomNumbers(datenumber, undlnumber, config.path)
    rnds.generate()

    # --------------  main  -----------------
    params_mc = params.copy()
    underlying_spots = []
    for underlying in product.underlyings:
        underlying_spot = marketdata.underlying[underlying].spot
        underlying_spots.append(underlying_spot)
        params_mc.__dict__[underlying] = [underlying_spot] * (datenumber+1)
    price = 0
    dt = config.dt
    sqrtdt = np.sqrt(dt)
    init_occur = defaultdict(int)
    event_dates = payoff.events.keys()

    # handling date = 0 event if any, for calculating theta
    if 0 in event_dates:
        for event in payoff.events[0]:
            if payoff.occur[event.__name__] > 1:
                res = event(params_mc, 0, 0)
                init_occur[event.__name__] += 1
            else:
                res = event(params_mc, 0)

            if isinstance(res, tuple):
                res, consequence = res
                if consequence == "KO":
                    return price
            price += res

    for pi in range(config.path):
        rnd_i = rnds.getrnd()
        price_i = 0
        KO_flag = False
        payoff._occur = init_occur.copy()

        for di in range(1, datenumber+1):
            # diffusion
            for ui, underlying in enumerate(product.underlyings):
                old = params_mc.__dict__[underlying][di-1]
                moneyness = old / underlying_spots[ui]
                vol = config.vol.calculate(underlying, moneyness, di)
                div = marketdata.underlying[underlying].div
                new = old * np.exp((marketdata.r - div - 0.5*vol*vol) * dt + vol * sqrtdt * rnd_i[ui, di - 1])
                params_mc.__dict__[underlying][di] = new

            # event handling
            if di in event_dates:
                for event in payoff.events[di]:
                    if payoff.occur[event.__name__]>1:
                        ei = payoff._occur[event.__name__]
                        res = event(params_mc, di, ei)
                        payoff._occur[event.__name__] += 1
                    else:
                        res = event(params_mc, di)

                    if isinstance(res, tuple):
                        res, consequence = res
                        if consequence == "KO":
                            price_i += res / np.exp(marketdata.r * (di-1) * dt) # TODO: prepare discounting factor
                            KO_flag = True
                    if res and not KO_flag: # If KO, then dont consider the event that happens later within same day
                        price_i += res / np.exp(marketdata.r * (di-1) * dt)

            # if knock out, break
            if KO_flag:
                break

        price += price_i / config.path
    print(f"finish pricing with time {time.time()-time0}")
    return price


class RandomNumbers():
    def __init__(self, d, n, p, method="numpy", antithetic=False):
        self.d = d
        self.n = n
        self.p = p
        self.method = "numpy"
        self.antithetic = antithetic
        self.rnd = None
        self.curd = 0

    def generate(self):
        if self.method == "numpy":
            if self.antithetic:
                d = self.d//2+1
                rnd_pos = np.random.randn(self.n*self.p, self.d)
                rnd_neg = -rnd_pos
                rnd = np.concatenate((rnd_pos,rnd_neg))
                self.rnd = rnd
            else:
                self.rnd = np.random.randn(self.n*self.p, self.d)

        self.curd = 0

    def getrnd(self):
        start = self.curd * self.n
        end = (self.curd+1) * self.n
        self.curd += 1
        return self.rnd[start:end]


