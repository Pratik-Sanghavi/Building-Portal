import pandas as pd
from datetime import datetime

def db_to_dataframe(db, dataframe_columns, db_columns):
    df = pd.DataFrame(columns=dataframe_columns)
    for entry in db:
        dict = {}
        for i in range(len(db_columns)):
            dict[dataframe_columns[i]] = getattr(entry, db_columns[i])
        df = df.append(dict, ignore_index=True)
    return df

def return_dates(db_col):
    to_dates = []
    for date in db_col:
        if date!=None:
            to_dates.append(datetime.strftime(date.date(), "%d %B %Y"))
        else:
            to_dates.append(None)
    return to_dates