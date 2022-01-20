import seaborn as sns


continuous_palette = sns.cubehelix_palette(30, start=.3, rot=0, reverse=True, light=.6)
alpha=.7
categorical_palette =  [( 172/256, 55/256, 246/256, alpha/2), ( 72/256, 169/256, 166/256, alpha), ( 33/256, 118/256, 174/256, alpha), ( 255/256, 140/256, 97/256, alpha), (92/256, 55/256, 76/256, alpha), ( 252/256, 186/256, 0, alpha), ( 221/256, 45/256, 74/256, alpha), ( 212/256, 175/256, 205/256, alpha), ( 18/256, 119/256, 219/256, alpha)]
# These are names of predined palettes from colorbrewer that can be used when you want to categorize colors on a chart into groups
multi_categorical_palette_names = ["Reds", "Blues", "Greens", "Greys", "Oranges", "PuRd", "GnBu", "YlOrRd", "BuGn", "Spectral"]
