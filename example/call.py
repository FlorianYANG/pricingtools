import exopricer as exo

product = exo.Product()

#### payoff
def call(p, date):
    S = p.S[date]
    K = p.K
    c = max(S-K, 0)
    return c  # payoff, KO
product.payoff.add(30, call) # today = 0

#### Params
params = product.params
params.K = 100

#### Market Data
md = exo.MarketData()
md.simple_update("S", type="Share", spot=100, vol=0.3, div=0.01)
md.r = 0.02
product.marketdata = md
product.underlyings = ["S"]

#### Config, default: MonteCarlo, dt = 1/256
c = product.config
c.path = 200000
c.antithetic = True
# c.with_greeks(all=True)


#### pricing

product.price()

print(product.result)
