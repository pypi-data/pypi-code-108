import pandas as pd

from ntiles import Ntile, PricingPortal

uni = pd.read_csv('/Users/alex/Documents/Notebook/improved_momentum/data/index/crsp_sp500/mapped_index.csv')
assets = uni.lpermno.astype(str).unique().tolist()
pricing_portal = PricingPortal(assets, '2015', '2016')
tile = Ntile(pricing_portal)
alpha = pricing_portal.delta_data.shift(1).stack()
tile.full_tear(alpha, ntiles=5, holding_period=2)
