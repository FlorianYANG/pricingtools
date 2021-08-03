import exopricer as exo
p = exo.Product()

#### payoff
def callspread(params, date):
    S = params.S[date]
    Kd = params.Kd
    Ku = params.Ku
    return max(S-Kd,0) - max(S-Ku,0) # payoff, KO

p.payoff.add(30, callspread)  # today = 0, dt = 1/256

#### Params
params = p.params
params.Kd = 100
params.Ku = 110


###u# Market Data
md = exo.MarketData()
md.simple_update("S", type="Share", spot=100, vol=0.3, div=0.00)
md.r = 0.02
p.marketdata = md
p.underlyings = ["S"]

#### Config, default: MonteCarlo, dt = 1/256
c = p.config
c.path = 10000
c.antithetic = True


#### pricing
p.price()

print(p.result)
