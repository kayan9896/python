#!pip install seaborn openpyxl pandas matplotlib        
import pandas as pd
import os
df = pd.read_excel(os.getcwd()+'/outcomes_incomes_fs.xlsx',skiprows=1)
import matplotlib.pyplot as plt


df=df.rename(index=df[df.columns[1]])
df_cor=df.loc[:,df.columns[2]:]
c=df_cor.T.corr()

pt=c[c.index.str.lower().str.contains('housekeeping')]
fig, axes = plt.subplots(nrows=1, ncols=3)

j=0
for i in pt.index:
    d=pt.loc[i,:].drop(i)
    d=d.sort_values(ascending=False,key=abs)
    print(d.head())
    d[:5].plot(figsize=(14,13),ax=axes[j],kind='bar')
    j+=1
                  
