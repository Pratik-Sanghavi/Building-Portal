import pandas as pd

def db_to_dataframe(db, dataframe_columns, db_columns):
    df = pd.DataFrame(columns=dataframe_columns)
    for entry in db:
        dict = {}
        for i in range(len(db_columns)):
            dict[dataframe_columns[i]] = getattr(entry, db_columns[i])
        # print(dict)
        df = df.append(dict, ignore_index=True)
    return df