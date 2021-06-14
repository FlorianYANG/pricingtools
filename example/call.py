import exopricer as exo

p = exo.Product()

#### payoff
def call(params, date):
    S = params.get("S", date)
    K = params.get("K")
    c = max(S-K, 0)
    return c  # payoff, KO
p.payoff.add(30, call) # today = 0

#### Params
params = {"K": 100}
p.params.add(params)

#### Market Data
md = exo.MarketData()
md.simple_update("S", type="Share", spot=100, vol=0.3, div=0.01)
md.r = 0.02
p.marketdata = md

#### Config, default: MonteCarlo, dt = 1/256
c = exo.Config()
c.path = 50000
c.antithetic = True
p.config = c

#### pricing
p.build(["S"])
res = p.price()

print(res)