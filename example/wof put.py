import exopricer as exo
import numpy as np

product = exo.Product()

#### payoff
def wof_put(p, date):
    S = np.min([p.S1[date], p.S2[date], p.S3[date]])
    K = p.K
    c = max(K-S, 0)
    return c  # payoff, KO
product.payoff.add(30, wof_put) # today = 0

#### Params
params = product.params
params.K = 100

#### Market Data
md = exo.MarketData()
md.simple_update("S1", type="Share", spot=100, vol=0.3, div=0.01, cor={"S2":0.9, "S3":0.8})
md.simple_update("S2", type="Share", spot=100, vol=0.3, div=0.01, cor={"S3":0.7})
md.simple_update("S3", type="Share", spot=100, vol=0.3, div=0.01)
md.r = 0.02
product.marketdata = md
product.underlyings = ["S1", "S2", "S3"]

#### Config, default: MonteCarlo, dt = 1/256
c = product.config
c.path = 10000
c.antithetic = True
# c.with_greeks(all=True)


#### pricing

product.price()

print(product.result)
