#!pip install pandas
import pandas as pd
import os

# Read the CSV file into a DataFrame
df = pd.read_csv(os.getcwd()+'/Spotify_2000.csv')
print(df.info())
df.head()
'''
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1994 entries, 0 to 1993
Data columns (total 15 columns):
 #   Column                  Non-Null Count  Dtype 
---  ------                  --------------  ----- 
 0   Index                   1994 non-null   int64 
 1   Title                   1994 non-null   object
 2   Artist                  1994 non-null   object
 3   Top Genre               1994 non-null   object
 4   Year                    1994 non-null   int64 
 5   Beats Per Minute (BPM)  1994 non-null   int64 
 6   Energy                  1994 non-null   int64 
 7   Danceability            1994 non-null   int64 
 8   Loudness (dB)           1994 non-null   int64 
 9   Liveness                1994 non-null   int64 
 10  Valence                 1994 non-null   int64 
 11  Length (Duration)       1994 non-null   object
 12  Acousticness            1994 non-null   int64 
 13  Speechiness             1994 non-null   int64 
 14  Popularity              1994 non-null   int64 
dtypes: int64(11), object(4)
memory usage: 233.8+ KB
None
Index	Title	Artist	Top Genre	Year	Beats Per Minute (BPM)	Energy	Danceability	Loudness (dB)	Liveness	Valence	Length (Duration)	Acousticness	Speechiness	Popularity
0	1	Sunrise	Norah Jones	adult standards	2004	157	30	53	-14	11	68	201	94	3	71
1	2	Black Night	Deep Purple	album rock	2000	135	79	50	-11	17	81	207	17	7	39
2	3	Clint Eastwood	Gorillaz	alternative hip hop	2001	168	69	66	-9	7	52	341	2	17	69
3	4	The Pretender	Foo Fighters	alternative metal	2007	173	96	43	-4	3	37	269	0	4	76
4	5	Waitin' On A Sunny Day	Bruce Springsteen	classic rock	2002	106	82	58	-5	10	87	256	
'''



# Find the non-numeric values in the 'Length (Duration)' column
non_numeric_values = pd.to_numeric(
    df['Length (Duration)'], errors='coerce'
).isnull()

# Get the unique non-numeric values
unique_non_numeric = df[non_numeric_values]['Length (Duration)'].unique()

# Print the non-numeric values
if len(unique_non_numeric) > 20:
  print(unique_non_numeric[:20])
else:
  print(unique_non_numeric)


'''                     
['1,412' '1,121' '1,367' '1,292']
'''

import math
# Clean and convert the Length (Duration) column to numeric.
df['Length (Duration)'] = (
    df['Length (Duration)'].astype(str).str.replace(',', '').astype(int)
)

def get_song_minutes(track_seconds):
  return math.floor(track_seconds / 60)

def get_song_seconds(track_seconds):
  return track_seconds % 60

# Get the length of the songs in minutes.
df['song_minutes'] = [get_song_minutes(x) for x in df['Length (Duration)']]
df['song_seconds'] = [get_song_seconds(x) for x in df['Length (Duration)']]

# Display a sample of the resulting table.
if df.shape[0] <= 20:
  print(df.to_markdown(index=False))
else:
  print(df[:3].to_markdown(index=False))

'''
|   Index | Title          | Artist      | Top Genre           |   Year |   Beats Per Minute (BPM) |   Energy |   Danceability |   Loudness (dB) |   Liveness |   Valence |   Length (Duration) |   Acousticness |   Speechiness |   Popularity |   song_minutes |   song_seconds |
|--------:|:---------------|:------------|:--------------------|-------:|-------------------------:|---------:|---------------:|----------------:|-----------:|----------:|--------------------:|---------------:|--------------:|-------------:|---------------:|---------------:|
|       1 | Sunrise        | Norah Jones | adult standards     |   2004 |                      157 |       30 |             53 |             -14 |         11 |        68 |                 201 |             94 |             3 |           71 |              3 |             21 |
|       2 | Black Night    | Deep Purple | album rock          |   2000 |                      135 |       79 |             50 |             -11 |         17 |        81 |                 207 |             17 |             7 |           39 |              3 |             27 |
|       3 | Clint Eastwood | Gorillaz    | alternative hip hop |   2001 |                      168 |       69 |             66 |              -9 |          7 |        52 |                 341 |              2 |            17 |           69 |              5 |             41 |
'''

# Combine the genre with song length.
df["Genre Duration"] = df["Top Genre"] + " - " + \
df["song_minutes"].astype(str) + ":" + df["song_seconds"].astype(str).str.zfill(2)

# Display a sample of the resulting table.
if df.shape[0] <= 20:
  print(df.to_markdown(index=False))
else:
  print(df[:3].to_markdown(index=False))

'''
|   Index | Title          | Artist      | Top Genre           |   Year |   Beats Per Minute (BPM) |   Energy |   Danceability |   Loudness (dB) |   Liveness |   Valence |   Length (Duration) |   Acousticness |   Speechiness |   Popularity |   song_minutes |   song_seconds |                        Genre Duration |
|--------:|:---------------|:------------|:--------------------|-------:|-------------------------:|---------:|---------------:|----------------:|-----------:|----------:|--------------------:|---------------:|--------------:|-------------:|---------------:|---------------:|-------------------------------------:|
|       1 | Sunrise        | Norah Jones | adult standards     |   2004 |                      157 |       30 |             53 |             -14 |         11 |        68 |                 201 |             94 |             3 |           71 |              3 |             21 |     adult standards - 3:21 |
|       2 | Black Night    | Deep Purple | album rock          |   2000 |                      135 |       79 |             50 |             -11 |         17 |        81 |                 207 |             17 |             7 |           39 |              3 |             27 |          album rock - 3:27 |
|       3 | Clint Eastwood | Gorillaz    | alternative hip hop |   2001 |                      168 |       69 |             66 |              -9 |          7 |        52 |                 341 |              2 |            17 |           69 |              5 |             41 | alternative hip hop - 5:41 |

'''

# Group the data on `Top Genre` and calculate the mean of `song_minutes` and `song_seconds`.
df_out = df.groupby('Top Genre')[['song_minutes', 'song_seconds']].mean()

# Round off the `song_seconds` to zero decimals.
df_out['song_seconds'] = df_out['song_seconds'].round(0).astype(int)

# Combine the `song_minutes` and `song_seconds` into a single column `Avg. Length (Duration)` in the format 'minutes:seconds'.
df_out['Avg. Length (Duration)'] = df_out['song_minutes'].astype(str) + ':' + df_out['song_seconds'].astype(str).str.zfill(2)

# Drop the `song_minutes` and `song_seconds` columns.
df_out.drop(columns=['song_minutes', 'song_seconds'], inplace=True)

# Sort the values in descending order of `Avg. Length (Duration)`
df_out = df_out.sort_values(by='Avg. Length (Duration)', ascending=False)

# Display the first 5 rows
print(df_out.head().to_markdown(numalign="left", stralign="left"))

# Print the column names and their data types
print(df_out.info())
'''
| Top Genre               | Avg. Length (Duration)   |
|:------------------------|:-------------------------|
| finnish metal           | 7.0:24                   |
| contemporary vocal jazz | 6.0:24                   |
| chamber pop             | 5.714285714285714:31     |
| italian pop             | 5.666666666666667:51     |
| funk                    | 5.230769230769231:40     |
<class 'pandas.core.frame.DataFrame'>
Index: 149 entries, finnish metal to rock-and-roll
Data columns (total 1 columns):
 #   Column                  Non-Null Count  Dtype 
---  ------                  --------------  ----- 
 0   Avg. Length (Duration)  149 non-null    object
dtypes: object(1)
memory usage: 2.3+ KB
None
'''
