import numpy as np
import time

def MonteCarlo(product):
    time0 = time.time()
    print("start pricing")

    undls = product.undls
    payoff = product.payoff
    config = product.config
    params = product.params
    md = product.marketdata

    # Prepare dates
    datenumber = max(payoff.dates)
    undlnumber = len(undls)

    # random varaible
    rnds = RandomNumbers(datenumber, undlnumber, config.path)
    rnds.generate()


    # main
    params_mc = params.copy()
    undl_spots = []
    for undl in product.undls:
        undl_spot = md.spot[undl]
        undl_spots.append(undl_spot)
        params_mc[undl] = [undl_spot] * (datenumber+1)
    price = 0
    dt = config.dt
    sqrtdt = np.sqrt(dt)

    for pi in range(config.path):
        rndi = rnds.getrnd()
        p_res = 0
        KO_flag = False

        for di in range(1, datenumber+1):
            # diffusion
            for ui, undl in enumerate(product.undls):
                old = params_mc[undl][di-1]
                moneyness = old / undl_spots[ui]
                vol = config.vol.calculate(undl, moneyness, di)
                div = md.div[undl]
                new = old * np.exp((md.r - div - 0.5*vol*vol)*dt + vol*sqrtdt*rndi[ui,di-1])
                params_mc.update(undl, new, di)

            # event handling
            todayevents = product.payoff[di]
            if todayevents:
                for event in todayevents:
                    res = event(params_mc, di)
                    if isinstance(res, tuple):
                        res, consequence = res
                        if consequence == "KO":
                            p_res += res
                            KO_flag = True
                    if res and not KO_flag: # If KO, then dont consider the event that happens later within same day
                        p_res += res
            if KO_flag:
                price += p_res / config.path
                break

        price += p_res / config.path
    print(f"finish pricing with time {time.time()-time0}")
    return price

def random():
    pass

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
