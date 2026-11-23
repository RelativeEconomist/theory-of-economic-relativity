"""Finite Diamond-Dybvig-inspired structural test; independent of TER/B mappings."""
from itertools import product, permutations
from fractions import Fraction as F

N=3
endowment=F(3)
early_promise=F(7,5)  # 1.4
insured_late=F(8,5)   # 1.6
reserve=F(6,5)        # 1.2, backed by ex ante taxes

def one_history(profile, rate=F(2), guarantee=False, queue=None):
    # profile for two patient depositors, first depositor impatient and always early
    early=[0]+[i+1 for i,a in enumerate(profile) if a=='D']
    late=[i+1 for i,a in enumerate(profile) if a=='W']
    order=tuple(early) if queue is None else tuple(queue)
    assert set(order)==set(early)
    asset=endowment
    claims=[F(0) for _ in range(N)]
    bank_early=[F(0) for _ in range(N)]
    # sequential service: each request paid at filing time up to liquidated assets
    for j in order:
        paid=min(asset,early_promise)
        asset-=paid
        bank_early[j]=paid
        claims[j]=paid
    # only assets not liquidated mature
    late_pool=asset*rate
    if late:
        for j in late:
            claims[j]=late_pool / len(late)
    # if no late depositors, no residual invested assets here
    bank_paid=sum(claims)
    funds=reserve if guarantee else F(0)
    public_topups=[F(0)]*N
    if guarantee:
        for j in early:
            due=early_promise-claims[j]
            public_topups[j]=due
        for j in late:
            due=max(F(0),insured_late-claims[j])
            public_topups[j]=due
        assert sum(public_topups)<=funds, (profile, order, public_topups)
        claims=[x+y for x,y in zip(claims,public_topups)]
    # bank+insurer+taxpaying household resources: unspent fiscal reserve stays with treasury
    assert sum(claims) <= endowment*rate+reserve  # weak global cap (liquidation destroys production)
    assert all(p>=0 for p in claims)
    return claims, sum(public_topups), bank_paid, asset

def expected(profile, rate=F(2), guarantee=False):
    early=[0]+[i+1 for i,a in enumerate(profile) if a=='D']
    ps=list(permutations(early))
    vec=[F(0)]*N
    pay=F(0)
    for queue in ps:
        claims,top,_,_=one_history(profile, rate, guarantee,queue)
        vec=[v+c/F(len(ps)) for v,c in zip(vec,claims)]
        pay+=top/F(len(ps))
    return vec,pay

def equilibrium(rate=F(2), guarantee=False):
    out=[]
    for p in product('WD',repeat=2):
        v,_=expected(p,rate,guarantee)
        is_ne=True
        for i in range(2):
            dev=list(p); dev[i] = 'W' if dev[i]=='D' else 'D'
            alt,_=expected(tuple(dev),rate,guarantee)
            if alt[i+1]>v[i+1]:is_ne=False
        if is_ne:out.append(''.join(p))
    return out

cases=[('Healthy',F(2),False),('Low long return',F(11,10),False),('Financed guarantee',F(2),True)]
for title,rate,guarantee in cases:
    print(title,'NE:',equilibrium(rate,guarantee))
    for p in product('WD',repeat=2):
        x,s=expected(p,rate,guarantee)
        print(''.join(p),'patient expected:',*[str(i) for i in x[1:]],'public payout',s)

assert equilibrium(F(2),False)==['WW','DD']
assert equilibrium(F(11,10),False)==['DD']
assert equilibrium(F(2),True)==['WW']
# Verify fund is sufficient for all queue permutations in guaranteed state
for p in product('WD',repeat=2):
    early=[0]+[i+1 for i,a in enumerate(p) if a=='D']
    for order in permutations(early):one_history(p,F(2),True,order)
print('ALL ASSERTIONS PASS')
