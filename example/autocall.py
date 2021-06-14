import exopricer as exo

p = exo.Product()

#### payoff
def recall(params, date, i):
    S = params.get("S", date)
    ko_limit = params.get("KOLimit", i)
    if S >= ko_limit:
        return params.get("Rebate", i), "KO"  # payoff, KO

for d in [10, 20, 30]:
    p.payoff.add(d, recall)

def put(params, date):
    S = params.get("S", date)
    K = params.get("K")
    p = max(K-S, 0)
    return -p  # payoff, KO

p.payoff.add(30, put) # today = 0


#### Params
params = {"K": 100, "KOLimit": [100, 98, 96], "Rebate": [1, 2, 3]}
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