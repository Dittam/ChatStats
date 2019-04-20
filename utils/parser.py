# April 11 2019
import json
import re
from functools import partial
import pandas as pd
from pandas.io.json import json_normalize
from sqlalchemy import create_engine

convert = {'👍': ':thumbsup:', '👎': ':thumbsdown:', '😆': ':joy:',
           '😍': ':heart_eyes:', '😠': ':angry:', '😢': ':disappointed_relieved:',
           '😮': ':astonished:'}

# ---fix facebook's wrong encoding for special chars and emojis---
fixFBEncoding = partial(re.compile(
    rb'\\u00([\da-f]{2})').sub, lambda m: bytes.fromhex(m.group(1).decode()))

# ---load json message archive---
path = "C:/Users/ditta/Desktop/Google_Interns_2019/message_1.json"
with open(path, 'rb') as binaryData:
    repaired = fixFBEncoding(binaryData.read())
data = json.loads(repaired.decode('utf8'))

df = json_normalize(data['messages'])  # load json into dataframe
# reverse order of dataframe and index so oldest messages at index 0
df = df.reindex(index=df.index[::-1])
df = df.reset_index(drop=True)

# ---write meassages dataframe to sql database in table Messages---
engine = create_engine('sqlite:///../ParsedData.db', echo=False)
connection = engine.connect()
df[["content", "sender_name", "timestamp_ms"]].to_sql(
    'Messages', con=connection, if_exists="replace")

# ---Generate Reactions table---
df = df[pd.notnull(df['reactions'])]  # remove messages with no reacts
reactDf = pd.DataFrame(columns=["messageIdx", "reactor", "reaction"])
# iterate over each reaction in each message and append to reactDf
for i, row in df[["reactions"]].iterrows():
    for react in row["reactions"]:
        reactDf.loc[len(reactDf)] = [i, react["actor"],
                                     convert[react["reaction"]]]

# ---write Reactions dataframe to sql database in table Reactions
reactDf.to_sql('Reactions', con=connection, if_exists="replace")


# reactDf.loc[reactDf["index"]==78830]