import exopricer as exo
p = exo.Product()

#### payoff
def call(params, date):
    S = params.get("S", date)
    Kd = params.get("Kd")
    Ku = params.get("Ku")
    return max(S-Kd,0) - max(S-Ku,0) # payoff, KO

p.payoff.add(30, call)  # today = 0, dt = 1/256

#### Params
params = {"Kd": 100, "Ku": 110}
p.params.add(params)

#### Market Data
md = exo.MarketData()
md.simple_update("S", type="Share", spot=100, vol=0.3, div=0.00)
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
