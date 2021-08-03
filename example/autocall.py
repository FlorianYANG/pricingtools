import exopricer as exo
import numpy as np

p = exo.Product()

def test():
    x,y = 1, 2
    return dict(**locals())
a = 1
a = test()

#### payoff
def recall(params, date, i):
    S = params.S[date]
    ko_limit = params.KOLimit[i]
    if S >= ko_limit:
        return params.Rebate[i], "KO"  # payoff, KO

p.payoff.add([30, 60, 90], recall)

def put(params, date):
    KI = np.min(params.S)
    S = params.S[date]
    K = params.K
    p = max(K-S, 0) * (KI<params.KILimit)
    return -p  # payoff, KO

p.payoff.add(90, put) # today = 0


#### Params
params = p.params
params.K = 100
params.KILimit = 80
params.KOLimit = [100, 98, 96]
params.Rebate = [1, 2, 3]

#### Market Data
md = exo.MarketData()
md.simple_update("S", type="Share", spot=100, vol=0.3, div=0.01)
md.r = 0.02
p.marketdata = md
p.underlyings = ["S"]

#### Config, default: MonteCarlo, dt = 1/256
c = exo.Config()
c.path = 10000
c.antithetic = True
p.config = c

#### pricing

p.price()

