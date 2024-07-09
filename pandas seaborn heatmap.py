#!pip install seaborn openpyxl pandas matplotlib        
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV files into Pandas Dataframes
df_1 = pd.read_excel('SOLDFOOD2023 - Winter.xlsx',sheet_name='JANUARY')
df_2 = pd.read_excel('SOLDFOOD2023 - Winter.xlsx',sheet_name='FEBRUARY')


columns=df_1.loc[2].values.tolist()
df_1=df_1.loc[3:]
df_1.columns=columns
df_1=df_1.groupby('GROUP')['QUANTITY'].sum()

columns=df_2.loc[2].values.tolist()
df_2=df_2.loc[3:]
df_2.columns=columns
df_2=df_2.groupby('GROUP')['QUANTITY'].sum()

df=pd.merge(df_1,df_2,on='GROUP')
df.columns=['Jan','Feb']

df=df.apply(pd.to_numeric, errors='coerce')
sns.heatmap(df, annot=True)

