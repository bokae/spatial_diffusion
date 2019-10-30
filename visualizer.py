#!/home/bokanyie/.anaconda3/bin/python

import pandas as pd
import sys
import json
import matplotlib.pyplot as plt

plt.rcParams["font.size"] = 18

nodelist = pd.read_csv('./vertices_fs.csv').set_index("id")
result = json.load(sys.stdin)
for k in result:
    nodelist[k] = nodelist.index.map({int(i): v for i, v in result[k]["time_infected"].items()})

timecols = ["month", *list(result.keys())]
nodelist.replace(0, None, inplace=True)

res = pd.DataFrame([nodelist.groupby(col).count()["cityid"].cumsum()/len(nodelist.index)*100 for col in timecols])
res.index = timecols
res = res.T

plt.figure(figsize=(10,7))
plt.plot(res.index, res["month"], 'r-',lw=3,label="Data")
for c in timecols[1:]:
    if c == timecols[1]:
        plt.plot(res.index,res[c],'-',lw=1,color='grey',label="ABMs")
    else:
        plt.plot(res.index,res[c],'-',lw=1,color='grey',label='')
plt.xlabel("Month")
plt.ylabel("% of nodes infected")
plt.legend()
plt.show()